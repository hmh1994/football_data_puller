import logging
from dataclasses import dataclass
from hashlib import md5

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.utils.type_helper.list_helper import find_first
from football_data_manager.merger.mergers.player import PlayerMerger
from football_data_manager.merger.services.translator import TranslatorService
from football_data_manager.puller.interfaces.pulselive.v1_match import (
    EventCardDict,
    EventGoalDict,
    EventSubDict,
    OfficialDict,
    V1EventResponse,
    V1MatchOfficialsResponse,
)
from football_data_manager.puller.interfaces.pulselive.v1_player import PlayerDetailResponse
from football_data_manager.puller.interfaces.pulselive.v2_match import (
    FormationDict,
    ManagerDict,
    PlayerSimpleDict,
    V2MatchResponse,
    V3MatchLineupResponse,
)
from football_data_manager.puller.pullers.pulselive.match import MatchPuller
from football_data_manager.puller.pullers.pulselive.player import PlayerPuller
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.officials import OfficialEntity
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.staffs import StaffEntity
from football_data_manager.repository.repositories.matches import MatchRepository
from football_data_manager.repository.repositories.officials import OfficialRepository
from football_data_manager.repository.repositories.players import PlayerRepository
from football_data_manager.repository.repositories.staffs import StaffRepository


logger = logging.getLogger(__name__)


@dataclass
class _LineupPlayerInfo:
    player: PlayerEntity
    position: PositionEnum
    shirt_number: int
    is_substitute: bool
    is_captain: bool


class MatchMerger:
    """Merge match detail/event/lineup/official responses into match entities."""

    _MATCH_REQUEST_PATH = "GET v2/matches/{match_id}"
    _EVENT_REQUEST_PATH = "GET v1/matches/{match_id}/events"
    _LINEUP_REQUEST_PATH = "GET v3/matches/{match_id}/lineups"

    def __init__(
        self,
        match_repo: MatchRepository,
        official_repo: OfficialRepository,
        player_repo: PlayerRepository,
        staff_repo: StaffRepository,
        translator: TranslatorService,
        player_puller: PlayerPuller,
        match_puller: MatchPuller,
        player_merger: PlayerMerger,
    ):
        self._match_repo = match_repo
        self._official_repo = official_repo
        self._player_repo = player_repo
        self._staff_repo = staff_repo
        self._translator = translator
        self._player_puller = player_puller
        self._match_puller = match_puller
        self._player_merger = player_merger

    async def merge_from_api(
        self,
        fixture: FixtureEntity,
        competition: CompetitionEntity,
        season: SeasonEntity,
    ) -> MatchEntity | None:
        """Pull 4 APIs then merge them into one match entity."""
        match_resp = await self._match_puller.pull_match(fixture.source_id)
        event_resp = await self._match_puller.pull_match_event(fixture.source_id)
        lineup_resp = await self._match_puller.pull_match_lineup(fixture.source_id)
        official_resp = await self._match_puller.pull_match_official(fixture.source_id)
        return await self.merge(
            fixture=fixture,
            competition=competition,
            season=season,
            match_response=match_resp,
            event_response=event_resp,
            lineup_response=lineup_resp,
            official_response=official_resp,
        )

    async def merge(
        self,
        fixture: FixtureEntity,
        competition: CompetitionEntity,
        season: SeasonEntity,
        match_response: V2MatchResponse,
        event_response: V1EventResponse,
        lineup_response: V3MatchLineupResponse,
        official_response: V1MatchOfficialsResponse,
    ) -> MatchEntity | None:
        """Merge already-fetched 4 match payloads into one match entity."""
        if season.competition_id != competition.id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        existing = await self._match_repo.get_by_pulselive_id(fixture.source_id)
        if existing is not None and existing.period == PeriodEnum.FULLTIME:
            return existing

        (
            home_lineup,
            home_subs,
            home_captain,
            home_players,
        ) = await self._extract_players(
            lineup_response.home_team["players"], competition, season
        )
        (
            away_lineup,
            away_subs,
            away_captain,
            away_players,
        ) = await self._extract_players(
            lineup_response.away_team["players"], competition, season
        )

        home_manager = await self._get_manager(lineup_response.home_team.get("managers", []))
        away_manager = await self._get_manager(lineup_response.away_team.get("managers", []))

        (
            referee,
            assistant_1,
            assistant_2,
            fourth,
            var,
            assistant_var,
        ) = await self._get_officials(official_response.match_officials)

        base_match = MatchEntity(
            attendance=match_response.attendance or 0,
            away_team_captain=away_captain,
            away_team_manager=away_manager,
            away_team_formation=self._parse_formation(lineup_response.away_team.get("formation")),
            away_team_score=match_response.away_team.get("score") or 0,
            away_team_half_time_score=match_response.away_team.get("half_time_score"),
            clock=self._to_int(match_response.clock),
            fixture=fixture,
            home_team_captain=home_captain,
            home_team_manager=home_manager,
            home_team_formation=self._parse_formation(lineup_response.home_team.get("formation")),
            home_team_score=match_response.home_team.get("score") or 0,
            home_team_half_time_score=match_response.home_team.get("half_time_score"),
            official_main_referee=referee,
            official_assistant_1_referee=assistant_1,
            official_assistant_2_referee=assistant_2,
            official_fourth_referee=fourth,
            official_var=var,
            official_assistant_var=assistant_var,
            period=PeriodEnum.from_string(match_response.period),
        )

        match = existing or base_match

        all_players = {
            player.source_id: player for player in (home_players + away_players)
        }

        self._log_goal_count_mismatch(
            match_source_id=fixture.source_id,
            match_response=match_response,
            event_response=event_response,
        )
        self._log_goal_scorer_lineup_mismatches(
            match_source_id=fixture.source_id,
            event_response=event_response,
            lineup_response=lineup_response,
        )

        # Lineup and bench
        for player_info in home_lineup:
            row_col = self._find_formation_position(
                lineup_response.home_team.get("formation", {}).get("lineup"),
                player_info.player.source_id,
            )
            if row_col is None:
                continue
            row, col = row_col
            match = await self._match_repo.append_lineup(
                match=match,
                is_home=True,
                player=player_info.player,
                position=player_info.position,
                shirt_number=player_info.shirt_number,
                row=row,
                column=col,
            )

        for player_info in away_lineup:
            row_col = self._find_formation_position(
                lineup_response.away_team.get("formation", {}).get("lineup"),
                player_info.player.source_id,
            )
            if row_col is None:
                continue
            row, col = row_col
            match = await self._match_repo.append_lineup(
                match=match,
                is_home=False,
                player=player_info.player,
                position=player_info.position,
                shirt_number=player_info.shirt_number,
                row=row,
                column=col,
            )

        for player_info in home_subs:
            match = await self._match_repo.append_substitute(
                match=match,
                is_home=True,
                player=player_info.player,
                position=player_info.position,
                shirt_number=player_info.shirt_number,
            )

        for player_info in away_subs:
            match = await self._match_repo.append_substitute(
                match=match,
                is_home=False,
                player=player_info.player,
                position=player_info.position,
                shirt_number=player_info.shirt_number,
            )

        # Events
        match = await self._append_cards(
            match,
            event_response.home_team.get("cards", []),
            is_home=True,
            player_map=all_players,
        )
        match = await self._append_cards(
            match,
            event_response.away_team.get("cards", []),
            is_home=False,
            player_map=all_players,
        )

        match = await self._append_goals(
            match,
            event_response.home_team.get("goals", []),
            is_home=True,
            player_map=all_players,
        )
        match = await self._append_goals(
            match,
            event_response.away_team.get("goals", []),
            is_home=False,
            player_map=all_players,
        )

        match = await self._append_substitutions(
            match,
            event_response.home_team.get("subs", []),
            is_home=True,
            player_map=all_players,
        )
        match = await self._append_substitutions(
            match,
            event_response.away_team.get("subs", []),
            is_home=False,
            player_map=all_players,
        )

        self._copy_match_fields(match, base_match)

        if existing is None:
            return await self._match_repo.create(match)
        return await self._match_repo.update(match)

    async def _extract_players(
        self,
        lineup_players: list[PlayerSimpleDict],
        competition: CompetitionEntity,
        season: SeasonEntity,
    ) -> tuple[
        list[_LineupPlayerInfo],
        list[_LineupPlayerInfo],
        PlayerEntity | None,
        list[PlayerEntity],
    ]:
        players: list[_LineupPlayerInfo] = []

        for item in lineup_players:
            player = await self._get_or_create_player(
                source_id=str(item["id"]),
                competition=competition,
                season=season,
            )
            if player is None:
                continue

            position_raw = item.get("position") or ""
            is_substitute = position_raw.lower() == "substitute"
            players.append(
                _LineupPlayerInfo(
                    player=player,
                    position=(
                        player.position
                        if is_substitute
                        else PositionEnum.from_string(position_raw)
                    ),
                    shirt_number=self._to_int(item.get("shirt_num")) or 0,
                    is_substitute=is_substitute,
                    is_captain=bool(item.get("is_captain")),
                )
            )

        lineup = [player for player in players if not player.is_substitute]
        subs = [player for player in players if player.is_substitute]
        captain = find_first(players, lambda p: p.is_captain)
        all_players = [player.player for player in players]
        return lineup, subs, captain.player if captain else None, all_players

    async def _get_or_create_player(
        self,
        source_id: str,
        competition: CompetitionEntity,
        season: SeasonEntity,
    ) -> PlayerEntity | None:
        player = await self._player_repo.get_by_pulselive_id(source_id)
        if player is not None:
            return player

        player_response = await self._player_puller.pull_player(source_id)
        target_detail = self._find_player_detail_for_context(
            player_response.root,
            competition_source_id=competition.source_id,
            season_source_id=season.source_id.split("_")[-1],
        )
        if target_detail is None and player_response.root:
            target_detail = player_response.root[0]

        if target_detail is None:
            return None

        return await self._player_merger.merge_player_detail(target_detail, season)

    @staticmethod
    def _find_player_detail_for_context(
        details: list[PlayerDetailResponse],
        competition_source_id: str,
        season_source_id: str,
    ) -> PlayerDetailResponse | None:
        for detail in details:
            competition_id = detail.id.get("competition_id")
            season_id = detail.id.get("season_id")
            if competition_id == competition_source_id and season_id == season_source_id:
                return detail
        return None

    async def _get_manager(self, managers: list[ManagerDict]) -> StaffEntity | None:
        manager = find_first(managers, lambda m: (m.get("type") or "").lower() == "manager")
        if manager is None:
            return None

        display_name = (manager.get("display") or "").strip()
        if not display_name:
            first_name = manager.get("first_name") or ""
            last_name = manager.get("last_name") or ""
            display_name = f"{first_name} {last_name}".strip()
        if not display_name:
            return None

        source_id = manager.get("id")
        if source_id:
            existing = await self._staff_repo.get_by_pulselive_id(str(source_id))
            if existing is not None:
                return existing
        else:
            existing = await self._staff_repo.get_by_display_name_en(display_name)
            if existing is not None:
                return existing

        if source_id is None:
            hashed = md5(display_name.encode("utf-8")).hexdigest()
            source_id = str(int(hashed, 16) % 2**16)

        created = StaffEntity(
            display_name_en=display_name,
            display_name_kr=await self._translator.translate_word(display_name),
            full_name=display_name,
            source_id=str(source_id),
        )
        result = await self._staff_repo.create(created)
        return result or await self._staff_repo.get_by_pulselive_id(str(source_id))

    async def _get_officials(
        self,
        officials: list[OfficialDict],
    ) -> tuple[
        OfficialEntity | None,
        OfficialEntity | None,
        OfficialEntity | None,
        OfficialEntity | None,
        OfficialEntity | None,
        OfficialEntity | None,
    ]:
        official_map: dict[str, OfficialEntity | None] = {}
        for item in officials:
            official_type = item["type"]
            official_map[official_type] = await self._get_or_create_official(item)

        return (
            official_map.get("Referee"),
            official_map.get("Assistant Referee#1"),
            official_map.get("Assistant Referee#2"),
            official_map.get("Fourth official"),
            official_map.get("Video Assistant Referee"),
            official_map.get("Assistant VAR Official"),
        )

    async def _get_or_create_official(self, item: OfficialDict) -> OfficialEntity | None:
        official = item.get("official")
        if not official:
            return None

        display_name = official.get("display", "").strip()
        if not display_name:
            return None

        existing = await self._official_repo.get_by_display_name_en(display_name)
        if existing is not None:
            return existing

        created = OfficialEntity(
            display_name_en=display_name,
            display_name_kr=await self._translator.translate_word(display_name),
            full_name=f"{official.get('first', '')} {official.get('last', '')}".strip() or display_name,
        )
        result = await self._official_repo.create(created)
        return result or await self._official_repo.get_by_display_name_en(display_name)

    async def _append_cards(
        self,
        match: MatchEntity,
        cards: list[EventCardDict],
        is_home: bool,
        player_map: dict[str, PlayerEntity],
    ) -> MatchEntity:
        for index, card in enumerate(cards):
            player_source_id = card.get("player_id")
            clock = self._to_int(card.get("time"))
            if not player_source_id or clock is None:
                continue

            player = player_map.get(player_source_id)
            if player is None:
                continue

            card_type_raw = card.get("type")
            if not card_type_raw:
                continue

            try:
                card_type = CardTypeEnum.from_string(card_type_raw)
            except ValueError:
                continue

            match = await self._match_repo.append_card(
                match=match,
                is_home=is_home,
                player=player,
                index=index,
                card_type=card_type,
                clock=clock,
            )

        return match

    async def _append_goals(
        self,
        match: MatchEntity,
        goals: list[EventGoalDict],
        is_home: bool,
        player_map: dict[str, PlayerEntity],
    ) -> MatchEntity:
        for index, goal in enumerate(goals):
            player_source_id = goal.get("player_id")
            clock = self._to_int(goal.get("time"))
            if not player_source_id or clock is None:
                continue

            player = player_map.get(player_source_id)
            if player is None:
                continue

            assist_player = None
            assist_source_id = goal.get("assist_player_id")
            if assist_source_id:
                assist_player = player_map.get(assist_source_id)

            goal_type = (goal.get("goal_type") or "").lower()
            match = await self._match_repo.append_goal(
                match=match,
                is_home=is_home,
                player=player,
                assist_player=assist_player,
                index=index,
                is_penalty=goal_type == "penalty",
                is_own_goal=goal_type == "own",
                clock=clock,
            )

        return match

    async def _append_substitutions(
        self,
        match: MatchEntity,
        substitutions: list[EventSubDict],
        is_home: bool,
        player_map: dict[str, PlayerEntity],
    ) -> MatchEntity:
        for sub in substitutions:
            in_source_id = sub.get("player_on_id")
            out_source_id = sub.get("player_off_id")
            clock = self._to_int(sub.get("time"))
            if not in_source_id or not out_source_id or clock is None:
                continue

            in_player = player_map.get(in_source_id)
            out_player = player_map.get(out_source_id)
            if in_player is None or out_player is None:
                continue

            match = await self._match_repo.append_substitution(
                match=match,
                is_home=is_home,
                in_player=in_player,
                out_player=out_player,
                clock=clock,
            )

        return match

    @staticmethod
    def _parse_formation(formation: FormationDict | None) -> list[int]:
        if formation is None:
            return []
        formation_str = formation.get("formation")
        if not formation_str:
            return []
        return [int(value) for value in formation_str.split("-") if value.isdigit()]

    @staticmethod
    def _find_formation_position(
        formation_lineup: list[list[str]] | None,
        player_source_id: str,
    ) -> tuple[int, int] | None:
        if formation_lineup is None:
            return None

        for row, lineup_row in enumerate(formation_lineup):
            for column, source_id in enumerate(lineup_row):
                if str(source_id) == str(player_source_id):
                    return row, column
        return None

    @staticmethod
    def _to_int(value: str | int | None) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _copy_match_fields(target: MatchEntity, source: MatchEntity) -> None:
        target.attendance = source.attendance
        target.away_team_captain_id = source.away_team_captain_id
        target.away_team_formation = source.away_team_formation
        target.away_team_half_time_score = source.away_team_half_time_score
        target.away_team_manager = source.away_team_manager
        target.away_team_score = source.away_team_score
        target.clock = source.clock
        target.home_team_captain_id = source.home_team_captain_id
        target.home_team_formation = source.home_team_formation
        target.home_team_half_time_score = source.home_team_half_time_score
        target.home_team_manager = source.home_team_manager
        target.home_team_score = source.home_team_score
        target.official_main_referee_id = source.official_main_referee_id
        target.official_assistant_1_referee_id = source.official_assistant_1_referee_id
        target.official_assistant_2_referee_id = source.official_assistant_2_referee_id
        target.official_fourth_referee_id = source.official_fourth_referee_id
        target.official_var_id = source.official_var_id
        target.official_assistant_var_id = source.official_assistant_var_id
        target.period = source.period

    @classmethod
    def _format_request_path(cls, template: str, match_source_id: str) -> str:
        return template.format(match_id=match_source_id)

    @classmethod
    def _log_goal_count_mismatch(
        cls,
        match_source_id: str,
        match_response: V2MatchResponse,
        event_response: V1EventResponse,
    ) -> None:
        home_goal_count = 0
        away_goal_count = 0

        for goal in event_response.home_team.get("goals", []):
            if (goal.get("goal_type") or "").lower() == "own":
                away_goal_count += 1
            else:
                home_goal_count += 1

        for goal in event_response.away_team.get("goals", []):
            if (goal.get("goal_type") or "").lower() == "own":
                home_goal_count += 1
            else:
                away_goal_count += 1

        home_score = match_response.home_team.get("score") or 0
        away_score = match_response.away_team.get("score") or 0
        if home_goal_count == home_score and away_goal_count == away_score:
            return

        logger.error(
            "Unfixable source data issue [issue=1] goal events and match score differ: "
            "match_source_id=%s home_goal_events=%s away_goal_events=%s "
            "home_team_score=%s away_team_score=%s match_request=%s event_request=%s",
            match_source_id,
            home_goal_count,
            away_goal_count,
            home_score,
            away_score,
            cls._format_request_path(cls._MATCH_REQUEST_PATH, match_source_id),
            cls._format_request_path(cls._EVENT_REQUEST_PATH, match_source_id),
        )

    @classmethod
    def _log_goal_scorer_lineup_mismatches(
        cls,
        match_source_id: str,
        event_response: V1EventResponse,
        lineup_response: V3MatchLineupResponse,
    ) -> None:
        home_player_ids = {
            str(player["id"]) for player in lineup_response.home_team.get("players", [])
        }
        away_player_ids = {
            str(player["id"]) for player in lineup_response.away_team.get("players", [])
        }

        for side, goals, valid_player_ids in (
            ("home", event_response.home_team.get("goals", []), home_player_ids),
            ("away", event_response.away_team.get("goals", []), away_player_ids),
        ):
            for index, goal in enumerate(goals):
                player_source_id = goal.get("player_id")
                if not player_source_id or player_source_id in valid_player_ids:
                    continue

                logger.error(
                    "Unfixable source data issue [issue=2] goal scorer missing from lineup/bench: "
                    "match_source_id=%s side=%s goal_index=%s goal_player_source_id=%s "
                    "event_request=%s lineup_request=%s",
                    match_source_id,
                    side,
                    index,
                    player_source_id,
                    cls._format_request_path(cls._EVENT_REQUEST_PATH, match_source_id),
                    cls._format_request_path(cls._LINEUP_REQUEST_PATH, match_source_id),
                )
