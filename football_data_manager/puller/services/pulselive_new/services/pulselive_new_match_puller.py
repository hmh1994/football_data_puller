from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.matches.match_repository import (
    MatchRepository,
)
from football_data_manager.common.repositories.officials.official_entity import (
    OfficialEntity,
)
from football_data_manager.common.repositories.officials.official_repository import (
    OfficialRepository,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.repositories.players.player_repository import (
    PlayerRepository,
)
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.repositories.staffs.staff_entity import (
    StaffEntity,
)
from football_data_manager.common.repositories.staffs.staff_repository import (
    StaffRepository,
)
from football_data_manager.common.services.common_service_container import (
    CommonServiceContainer,
)
from football_data_manager.common.services.translator.translatorService import (
    TranslatorService,
)
from football_data_manager.common.utils.type_helper.list_helper import find_first
from football_data_manager.puller.services.pulselive_new.components.pulselive_new_webclient import (
    PulseliveNewWebclient,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_event_card_response import (
    PulseliveNewEventCardResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_event_goal_response import (
    PulseliveNewEventGoalResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_event_sub_response import (
    PulseliveNewEventSubResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_manager_response import (
    PulseliveNewManagerResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_match_lineup_formation_response import (
    PulseliveNewFormationResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_official_response import (
    PulseliveNewOfficialResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_person_response import (
    PulseliveNewPersonResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_player_simple_response import (
    PulseliveNewPlayerSimpleResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_event_response import (
    PulseliveNewV1EventResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_match_officials_response import (
    PulseliveNewV1MatchOfficialsResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v2_match_response import (
    PulseliveNewV2MatchResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v3_match_lineup_response import (
    PulseliveNewV3MatchLineupResponse,
)
from football_data_manager.puller.services.pulselive_new.services.pulselive_new_player_puller import (
    PulseliveNewPlayerPuller,
)


class PulseliveNewMatchPuller:

    __match_repository: MatchRepository
    __official_repository: OfficialRepository
    __player_repository: PlayerRepository
    __season_repository: SeasonRepository
    __staff_repository: StaffRepository
    __translator: TranslatorService
    __webclient: PulseliveNewWebclient
    __player_puller: PulseliveNewPlayerPuller

    class __PlayerInfo:
        def __init__(
            self,
            player: PlayerEntity,
            position: PositionEnum,
            shirt_number: int,
            is_substitute: bool,
            is_captain: bool,
        ):
            self.player = player
            self.position = position
            self.shirt_number = shirt_number
            self.is_substitute = is_substitute
            self.is_captain = is_captain

    def __init__(
        self,
        service_container: CommonServiceContainer,
        repository_container: CommonRepositoryContainer,
        pulselive_service: PulseliveNewWebclient,
        player_puller: PulseliveNewPlayerPuller,
    ):
        self.__match_repository = repository_container.match_repository()
        self.__official_repository = repository_container.official_repository()
        self.__player_repository = repository_container.player_repository()
        self.__staff_repository = repository_container.staff_repository()
        self.__translator = service_container.translator_service()
        self.__webclient = pulselive_service
        self.__player_puller = player_puller

    async def pull_match(
        self,
        fixture: FixtureEntity,
        competition: CompetitionEntity,
        season: SeasonEntity,
    ) -> MatchEntity | None:
        if competition.id != season.competition_id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )
        if fixture.season_id != season.id:
            raise ValueError(
                f"Fixture {fixture.id} does not belong to season {season.id}"
            )

        match = await self.__match_repository.read_by_pulselive_id(fixture.source_id)
        if match is not None:
            return match

        match_info = await self.__webclient.get_v2_match(fixture.source_id)
        events = await self.__webclient.get_v1_match_event(fixture.source_id)
        lineup = await self.__webclient.get_v3_match_lineup(fixture.source_id)
        officials = await self.__webclient.get_v1_match_official(fixture.source_id)
        match = await self.__process_match(
            fixture, competition, season, match_info, events, lineup, officials
        )
        return await self.__match_repository.create(match)

    async def __process_match(
        self,
        fixture: FixtureEntity,
        competition: CompetitionEntity,
        season: SeasonEntity,
        match_info: PulseliveNewV2MatchResponse,
        events: PulseliveNewV1EventResponse,
        lineup: PulseliveNewV3MatchLineupResponse,
        officials: PulseliveNewV1MatchOfficialsResponse,
    ) -> MatchEntity:
        (
            (home_lineup_players, home_substitute_players, home_captain),
            (away_lineup_players, away_substitute_players, away_captain),
            home_manager,
            away_manager,
            (
                referee,
                assistant_1_referee,
                assistant_2_referee,
                fourth_referee,
                var,
                assistant_var,
            ),
        ) = (
            await self.__get_players(lineup.home_team.players, competition, season),
            await self.__get_players(lineup.away_team.players, competition, season),
            await self.__get_manager(lineup.home_team.managers),
            await self.__get_manager(lineup.away_team.managers),
            await self.__get_officials(officials.match_officials),
        )
        match = MatchEntity(
            attendance=match_info.attendance,
            away_team_captain=away_captain,
            away_team_manager=away_manager,
            away_team_formation=self.__get_formation(lineup.away_team.formation),
            away_team_score=match_info.away_team.score,
            away_team_half_time_score=match_info.away_team.half_time_score,
            clock=int(match_info.clock) if match_info.clock else None,
            fixture=fixture,
            home_team_captain=home_captain,
            home_team_manager=home_manager,
            home_team_formation=self.__get_formation(lineup.home_team.formation),
            home_team_score=match_info.home_team.score,
            home_team_half_time_score=match_info.home_team.half_time_score,
            official_main_referee=referee,
            official_assistant_1_referee=assistant_1_referee,
            official_assistant_2_referee=assistant_2_referee,
            official_fourth_referee=fourth_referee,
            official_var=var,
            official_assistant_var=assistant_var,
            period=PeriodEnum.from_string(match_info.period),
        )
        home_players = [p.player for p in home_lineup_players + home_substitute_players]
        away_players = [p.player for p in away_lineup_players + away_substitute_players]
        all_players = home_players + away_players
        for player_info in home_lineup_players:
            match = await self.__update_lineup(
                match, player_info, True, lineup.home_team.formation.lineup
            )
        for player_info in home_substitute_players:
            match = await self.__match_repository.append_substitute(
                match,
                True,
                player_info.player,
                player_info.position,
                player_info.shirt_number,
            )
        for idx, card_info in enumerate(events.home_team.cards):
            match = await self.__update_card(match, idx, card_info, True, home_players)
        # Filter valid goal events for home team
        valid_home_goals = [
            goal for goal in events.home_team.goals if goal.is_valid_event()
        ]
        for idx, goal_info in enumerate(valid_home_goals):
            match = await self.__update_goal(match, idx, goal_info, True, all_players)
        # Fill in substitutions for home team
        valid_home_subs = [sub for sub in events.home_team.subs if sub.is_valid_event()]
        for sub_info in valid_home_subs:
            match = await self.__update_substitution(
                match, sub_info, True, home_players
            )
        for player_info in away_lineup_players:
            match = await self.__update_lineup(
                match, player_info, False, lineup.away_team.formation.lineup
            )
        for player_info in away_substitute_players:
            match = await self.__match_repository.append_substitute(
                match,
                False,
                player_info.player,
                player_info.position,
                player_info.shirt_number,
            )
        for idx, card_info in enumerate(events.away_team.cards):
            match = await self.__update_card(match, idx, card_info, False, away_players)
        # Filter valid goal events for away team
        valid_away_goals = [
            goal for goal in events.away_team.goals if goal.is_valid_event()
        ]
        for idx, goal_info in enumerate(valid_away_goals):
            match = await self.__update_goal(match, idx, goal_info, False, all_players)
        # Fill in substitutions for away team
        valid_away_subs = [sub for sub in events.away_team.subs if sub.is_valid_event()]
        for sub_info in valid_away_subs:
            match = await self.__update_substitution(
                match, sub_info, False, away_players
            )
        return match

    async def __get_players(
        self,
        lineup: list[PulseliveNewPlayerSimpleResponse],
        competition: CompetitionEntity,
        season: SeasonEntity,
    ) -> tuple[
        list[__PlayerInfo],
        list[__PlayerInfo],
        PlayerEntity | None,
    ]:
        """
        Get players from lineup with fixture context for player creation.

        :param lineup: List of player information from match lineup
        :param competition: Competition entity for context validation
        :param season: Season entity for context validation
        :returns: Tuple of (lineup_players, substitute_players, captain)
        """
        players = []
        for player in lineup:
            player_info = await self.__get_player(player, competition, season)
            players.append(player_info)
        captain = find_first(players, lambda p: p.is_captain)
        return (
            [p for p in players if not p.is_substitute],
            [p for p in players if p.is_substitute],
            captain.player,
        )

    async def __get_manager(
        self, manager_info_list: list[PulseliveNewManagerResponse]
    ) -> StaffEntity | None:
        """
        Get manager from staff list, ensuring all staff are in repository.

        Checks if all staff from manager_info_list exist in the staff repository.
        Creates any missing staff entities, then returns the staff member with
        type "Manager".

        :param manager_info_list: List of manager/staff information from PulseLive API
        :returns: Staff entity with Manager type
        :raises ValueError: If no manager is found in the list
        """
        # Check all staff members and collect missing ones
        missing_staff = []
        manager_staff = None

        for staff_info in manager_info_list:
            if not staff_info.is_valid_event():
                continue

            # Check if staff exists in repository
            existing_staff = await self.__staff_repository.read_by_pulselive_id(
                staff_info.id
            )

            if existing_staff is None:
                # Create new staff entity for missing staff
                new_staff = StaffEntity(
                    display_name_en=staff_info.simple_name,
                    display_name_kr=await self.__translator.translate_word(
                        staff_info.simple_name
                    ),
                    full_name=staff_info.full_name,
                    source_id=str(staff_info.id),
                )
                missing_staff.append(new_staff)

                # Track the manager entity
                if staff_info.type == "Manager":
                    manager_staff = new_staff
            else:
                # Use existing staff if it's the manager
                if staff_info.type == "Manager":
                    manager_staff = existing_staff

        # Create all missing staff in batch
        if missing_staff:
            await self.__staff_repository.create_all(missing_staff)

        return manager_staff

    async def __get_officials(
        self, officials_info_list: list[PulseliveNewOfficialResponse]
    ) -> tuple[
        OfficialEntity | None,
        OfficialEntity | None,
        OfficialEntity | None,
        OfficialEntity | None,
        OfficialEntity | None,
        OfficialEntity | None,
    ]:
        # Get referee
        referee_info = find_first(
            officials_info_list, lambda info: info.type == "Referee"
        )
        referee = (
            await self.__get_official(referee_info.official) if referee_info else None
        )
        # Get assistant #1 referee
        assistant_1_referee_info = find_first(
            officials_info_list, lambda info: info.type == "Assistant Referee#1"
        )
        assistant_1_referee = (
            await self.__get_official(assistant_1_referee_info.official)
            if assistant_1_referee_info
            else None
        )
        # Get assistant #2 referee
        assistant_2_referee_info = find_first(
            officials_info_list, lambda info: info.type == "Assistant Referee#2"
        )
        assistant_2_referee = (
            await self.__get_official(assistant_2_referee_info.official)
            if assistant_2_referee_info
            else None
        )
        # Get fourth official
        fourth_official = find_first(
            officials_info_list, lambda info: info.type == "Fourth official"
        )
        fourth_official = (
            await self.__get_official(fourth_official.official)
            if fourth_official
            else None
        )
        # Get VAR
        var_info = find_first(
            officials_info_list, lambda info: info.type == "Video Assistant Referee"
        )
        var = await self.__get_official(var_info.official) if var_info else None
        # Get Assistant VAR
        assistant_var_info = find_first(
            officials_info_list,
            lambda info: info.type == "Assistant VAR Official",
        )
        assistant_var = (
            await self.__get_official(assistant_var_info.official)
            if assistant_var_info
            else None
        )
        return (
            referee,
            assistant_1_referee,
            assistant_2_referee,
            fourth_official,
            var,
            assistant_var,
        )

    async def __update_lineup(
        self,
        match: MatchEntity,
        player_info: __PlayerInfo,
        is_home: bool,
        formation: list[list[str]],
    ) -> MatchEntity:
        row, col = None, None
        for r, row_formation in enumerate(formation):
            for c, player_id in enumerate(row_formation):
                if player_id == player_info.player.source_id:
                    row, col = r, c
                    break
        if row is None or col is None:
            return match
        return await self.__match_repository.append_lineup(
            match=match,
            is_home=is_home,
            player=player_info.player,
            position=player_info.position,
            shirt_number=player_info.shirt_number,
            row=row,
            column=col,
        )

    async def __update_card(
        self,
        match: MatchEntity,
        index: int,
        card_info: PulseliveNewEventCardResponse,
        is_home: bool,
        player_list: list[PlayerEntity],
    ) -> MatchEntity:
        if card_info.player_id is None:
            return match
        player = find_first(player_list, lambda p: p.source_id == card_info.player_id)
        return await self.__match_repository.append_card(
            match=match,
            is_home=is_home,
            player=player,
            index=index,
            card_type=CardTypeEnum.from_string(card_info.type),
            clock=int(card_info.time),
        )

    async def __update_goal(
        self,
        match: MatchEntity,
        index: int,
        goal_info: PulseliveNewEventGoalResponse,
        is_home: bool,
        player_list: list[PlayerEntity],
    ) -> MatchEntity:
        player = find_first(player_list, lambda p: p.source_id == goal_info.player_id)
        assist_player = find_first(
            player_list, lambda p: p.source_id == goal_info.assist_player_id
        )
        # TODO: Process Own Goal
        return await self.__match_repository.append_goal(
            match=match,
            is_home=is_home,
            player=player,
            assist_player=assist_player,
            index=index,
            is_penalty=goal_info.goal_type == "Penalty",
            is_own_goal=goal_info.goal_type == "Own",
            clock=int(goal_info.time),
        )

    async def __update_substitution(
        self,
        match: MatchEntity,
        sub_info: PulseliveNewEventSubResponse,
        is_home: bool,
        player_list: list[PlayerEntity],
    ) -> MatchEntity:
        in_player = find_first(
            player_list, lambda p: p.source_id == sub_info.player_on_id
        )
        out_player = find_first(
            player_list, lambda p: p.source_id == sub_info.player_off_id
        )
        if in_player is None or out_player is None:
            raise ValueError(
                f"Substitution players not found: {sub_info.player_on_id}, {sub_info.player_off_id}"
            )
        return await self.__match_repository.append_substitution(
            match=match,
            is_home=is_home,
            in_player=in_player,
            out_player=out_player,
            clock=int(sub_info.time),
        )

    async def __get_player(
        self,
        player_info: PulseliveNewPlayerSimpleResponse,
        competition: CompetitionEntity,
        season: SeasonEntity,
    ) -> __PlayerInfo:
        """
        Get player entity, creating from PulseLive API if not found.

        Attempts to find existing player by PulseLive ID. If not found, fetches
        player data from PulseLive v1 player API, validates it matches the current
        match context, and creates the player entity with proper translations.

        :param player_info: Player information from match lineup
        :param competition: Competition entity for context validation
        :param season: Season entity for context validation
        :returns: Tuple of (player, shirt_number, is_substitute, is_captain)
        :raises ValueError: If player context doesn't match or creation fails
        """
        player = await self.__player_repository.read_by_pulselive_id(player_info.id)

        if player is None:
            # Fetch player data from PulseLive API
            try:
                player_data_list = await self.__webclient.get_v1_player(player_info.id)
                player_data = None
                for player_season_data in player_data_list.root:
                    # Find the player data that matches the current competition and season
                    if (
                        player_season_data.id.competition_id == competition.source_id
                        and player_season_data.id.season_id == season.season_source_id
                    ):
                        player_data = player_season_data
                        break

                # Validate player belongs to correct competition and season
                if player_data is None:
                    raise ValueError(
                        f"Player {player_info.simple_name}({player_info.id}) competition/season mismatch. "
                        f"Expected: {competition.source_id}/{season.season_source_id}"
                    )
                player = await self.__player_puller.process_player(player_data)
                if player is None:
                    raise ValueError(
                        f"Failed to create player entity for ID: {player_info.id}"
                    )

            except Exception as e:
                raise ValueError(
                    f"Failed to fetch or create player {player_info.id}: {e}"
                )

        is_substitute = player_info.position == "Substitute"
        return self.__PlayerInfo(
            player=player,
            position=(
                player.position
                if is_substitute
                else PositionEnum.from_string(player_info.position)
            ),
            shirt_number=int(player_info.shirt_num),
            is_substitute=is_substitute,
            is_captain=player_info.is_captain,
        )

    async def __get_official(
        self, official_info: PulseliveNewPersonResponse
    ) -> OfficialEntity:
        official = await self.__official_repository.read_by_display_name_en(
            official_info.simple_name
        )
        if official is None:
            official = OfficialEntity(
                display_name_en=official_info.simple_name,
                display_name_kr=await self.__translator.translate_word(
                    official_info.simple_name
                ),
                full_name=official_info.full_name,
            )
            official = await self.__official_repository.create(official)
        return official

    @staticmethod
    def __get_formation(formation_info: PulseliveNewFormationResponse) -> list[int]:
        if formation_info.formation is None:
            return []
        return [int(f) for f in formation_info.formation.split("-")]
