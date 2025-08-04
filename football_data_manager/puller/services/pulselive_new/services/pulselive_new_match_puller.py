from asyncio import gather

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
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


class PulseliveNewMatchPuller:

    __match_repository: MatchRepository
    __official_repository: OfficialRepository
    __player_repository: PlayerRepository
    __staff_repository: StaffRepository
    __translator: TranslatorService
    __webclient: PulseliveNewWebclient

    def __init__(
        self,
        service_container: CommonServiceContainer,
        repository_container: CommonRepositoryContainer,
        pulselive_service: PulseliveNewWebclient,
    ):
        self.__match_repository = repository_container.match_repository()
        self.__official_repository = repository_container.official_repository()
        self.__player_repository = repository_container.player_repository()
        self.__staff_repository = repository_container.staff_repository()
        self.__translator = service_container.translator_service()
        self.__webclient = pulselive_service

    async def pull(self, fixture: FixtureEntity) -> MatchEntity:
        match_info, events, lineup, officials = await gather(
            self.__webclient.get_v2_match(fixture.source_id),
            self.__webclient.get_v1_match_event(fixture.source_id),
            self.__webclient.get_v3_match_lineup(fixture.source_id),
            self.__webclient.get_v1_match_official(fixture.source_id),
        )
        match = await self.__process_match(
            fixture, match_info, events, lineup, officials
        )
        return await self.__match_repository.create(match)

    async def __process_match(
        self,
        fixture: FixtureEntity,
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
        ) = await gather(
            self.__get_players(lineup.home_team.players),
            self.__get_players(lineup.away_team.players),
            self.__get_manager(lineup.home_team.managers),
            self.__get_manager(lineup.away_team.managers),
            self.__get_officials(officials.match_officials),
        )
        match = MatchEntity(
            attendance=match_info.attendance,
            away_team_captain=away_captain,
            away_team_manager=away_manager,
            away_team_formation=self.__get_formation(lineup.away_team.formation),
            away_team_score=match_info.away_team.score,
            away_team_half_time_score=match_info.away_team.half_time_score,
            clock=int(match_info.clock),
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
        )
        home_players = [p for p, _ in home_lineup_players + home_substitute_players]
        for player, shirt_number in home_lineup_players:
            match = await self.__update_lineup(
                match, player, shirt_number, True, lineup.home_team.formation.lineup
            )
        for player, shirt_number in home_substitute_players:
            match = await self.__match_repository.append_substitute(
                match, True, player, shirt_number
            )
        for card_info in events.home_team.cards:
            match = await self.__update_card(match, card_info, True, home_players)
        for goal_info in events.home_team.goals:
            match = await self.__update_goal(match, goal_info, True, home_players)
        for sub_info in events.home_team.subs:
            match = await self.__update_substitution(
                match, sub_info, True, home_players
            )
        away_players = [p for p, _ in away_lineup_players + away_substitute_players]
        for player, shirt_number in away_lineup_players:
            match = await self.__update_lineup(
                match, player, shirt_number, False, lineup.away_team.formation.lineup
            )
        for player, shirt_number in away_substitute_players:
            match = await self.__match_repository.append_substitute(
                match, False, player, shirt_number
            )
        for card_info in events.away_team.cards:
            match = await self.__update_card(match, card_info, False, away_players)
        for goal_info in events.away_team.goals:
            match = await self.__update_goal(match, goal_info, False, away_players)
        for sub_info in events.away_team.subs:
            match = await self.__update_substitution(
                match, sub_info, False, away_players
            )
        return match

    async def __get_players(
        self,
        lineup: list[PulseliveNewPlayerSimpleResponse],
    ) -> tuple[
        list[tuple[PlayerEntity, int]],
        list[tuple[PlayerEntity, int]],
        PlayerEntity | None,
    ]:
        players: list[tuple[PlayerEntity, int, bool, bool]] = await gather(
            *[self.__get_player(player) for player in lineup]
        )
        captain = find_first(players, lambda player: player[1])
        if captain is not None:
            return (
                [(p, num) for p, num, is_sub, _ in players if not is_sub],
                [(p, num) for p, num, is_sub, _ in players if is_sub],
                captain[0],
            )
        else:
            raise ValueError("No captain found in the lineup.")

    async def __get_manager(
        self, manager_info_list: list[PulseliveNewManagerResponse]
    ) -> StaffEntity:
        manager_info = find_first(manager_info_list, lambda m: m.type == "Manager")
        if manager_info is None:
            raise ValueError("Manager not found in the lineup.")
        manager = await self.__staff_repository.read_by_pulselive_id(manager_info.id)
        if manager is None:
            # TODO: Remove this and raise an error if the manager is not found.
            staff_list = list()
            for staff_info in manager_info_list:
                staff = StaffEntity(
                    display_name_en=staff_info.simple_name,
                    display_name_kr=await self.__translator.translate_word(
                        staff_info.simple_name
                    ),
                    full_name=staff_info.full_name,
                    source_id=str(staff_info.id),
                )
                staff_list.append(staff)
                if staff_info.type == "Manager":
                    manager = staff
            await self.__staff_repository.create_all(staff_list)
        return manager

    async def __get_officials(
        self, officials_info_list: list[PulseliveNewOfficialResponse]
    ) -> tuple[
        OfficialEntity,
        OfficialEntity,
        OfficialEntity,
        OfficialEntity,
        OfficialEntity | None,
        OfficialEntity | None,
    ]:
        referee_info = find_first(
            officials_info_list, lambda info: info.type == "Referee"
        )
        if referee_info is None:
            raise ValueError("Referee not found in the officials list.")
        referee = await self.__get_official(referee_info.official)
        assistant_1_referee_info = find_first(
            officials_info_list, lambda info: info.type == "Assistant Referee#1"
        )
        if assistant_1_referee_info is None:
            raise ValueError("Assistant Referee#1 not found in the officials list.")
        assistant_1_referee = await self.__get_official(
            assistant_1_referee_info.official
        )
        assistant_2_referee_info = find_first(
            officials_info_list, lambda info: info.type == "Assistant Referee#2"
        )
        if assistant_2_referee_info is None:
            raise ValueError("Assistant Referee#2 not found in the officials list.")
        assistant_2_referee = await self.__get_official(
            assistant_2_referee_info.official
        )
        fourth_official = find_first(
            officials_info_list, lambda info: info.type == "Fourth official"
        )
        if fourth_official is None:
            raise ValueError("Fourth Official not found in the officials list.")
        fourth_official = await self.__get_official(fourth_official.official)
        var_info = find_first(
            officials_info_list, lambda info: info.type == "Video Assistant Referee"
        )
        var = await self.__get_official(var_info.official) if var_info else None
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
        player: PlayerEntity,
        shirt_number: int,
        is_home: bool,
        formation: list[list[str]],
    ) -> MatchEntity:
        row, col = None, None
        for r, row_formation in enumerate(formation):
            for c, player_id in enumerate(row_formation):
                if player_id == player.source_id:
                    row, col = r, c
                    break
        if row is None or col is None:
            raise ValueError(
                f"Player {player.display_name_en} not found in the formation."
            )
        return await self.__match_repository.append_lineup(
            match=match,
            is_home=is_home,
            player=player,
            shirt_number=shirt_number,
            row=row,
            column=col,
        )

    async def __update_card(
        self,
        match: MatchEntity,
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
            card_type=CardTypeEnum.from_string(card_info.type),
            clock=int(card_info.time),
        )

    async def __update_goal(
        self,
        match: MatchEntity,
        goal_info: PulseliveNewEventGoalResponse,
        is_home: bool,
        player_list: list[PlayerEntity],
    ) -> MatchEntity:
        player = find_first(player_list, lambda p: p.source_id == goal_info.player_id)
        assist_player = find_first(
            player_list, lambda p: p.source_id == goal_info.assist_player_id
        )
        return await self.__match_repository.append_goal(
            match=match,
            is_home=is_home,
            player=player,
            assist_player=assist_player,
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
        self, player_info: PulseliveNewPlayerSimpleResponse
    ) -> tuple[PlayerEntity, int, bool, bool]:
        # TODO: Remove this and find player by ID.
        player = await self.__player_repository.read_by_display_name_en(
            player_info.simple_name
        )
        if player is None:
            player = await self.__player_repository.read_by_full_name(
                player_info.full_name
            )
        if player is None:
            raise ValueError(
                f"Player not found: {player_info.simple_name} ({player_info.full_name})"
            )
        if player.source_id != player_info.id:
            player.source_id = str(player_info.id)
            player = await self.__player_repository.update(player)
        return (
            player,
            int(player_info.shirt_num),
            player_info.position == "Substitute",
            player_info.is_captain,
        )

    async def __get_official(
        self, official_info: PulseliveNewPersonResponse
    ) -> OfficialEntity:
        official = await self.__official_repository.read_by_display_name_en(
            official_info.simple_name
        )
        if official is None:
            # TODO: Remove this and raise an error if the official is not found.
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
        return [int(f) for f in formation_info.formation.split("-")]
