from asyncio import gather

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.new_repositories.match_stats.match_stat_entity import (
    MatchStatEntity,
)
from football_data_manager.common.new_repositories.match_stats.match_stat_repository import (
    MatchStatRepository,
)
from football_data_manager.common.new_repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.new_repositories.matches.match_repository import (
    MatchRepository,
)
from football_data_manager.common.new_repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.puller.services.pulselive.models.responses.match_stats.pulselive_match_stat_item_response import (
    PulseliveMatchStatItemResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.match_stats.pulselive_match_stat_response import (
    PulseliveMatchStatResponse,
)
from football_data_manager.puller.services.pulselive.services.pulselive_web_client_service import (
    PulseliveWebClientService,
)


class PulseliveStatsMatchService:

    __match_repository: MatchRepository
    __match_stat_repository: MatchStatRepository
    __team_repository: TeamRepository
    __web_client: PulseliveWebClientService

    def __init__(
        self,
        db_service: DbService,
        pulselive_service: PulseliveWebClientService,
    ):
        self.__match_repository = MatchRepository(db_service)
        self.__match_stat_repository = MatchStatRepository(db_service)
        self.__team_repository = TeamRepository(db_service)
        self.__web_client = pulselive_service

    async def pull_match_stat(self, match: MatchEntity):
        match_stat = await self.__web_client.get_football_stats_match(
            int(match.source_id)
        )
        home_match_stat, away_match_stat = self.__process_match_stat(match, match_stat)
        await self.__match_stat_repository.create_all(
            [home_match_stat, away_match_stat]
        )

    async def __process_match_stat(
        self,
        match: MatchEntity,
        match_stat: PulseliveMatchStatResponse,
    ) -> tuple[MatchStatEntity, MatchStatEntity]:
        home_team, away_team = await gather(
            self.__team_repository.read_by_source_id(
                SourceEnum.PULSELIVE, match_stat.entity.teams[0].team.id
            ),
            self.__team_repository.read_by_source_id(
                SourceEnum.PULSELIVE, match_stat.entity.teams[1].team.id
            ),
        )
        home_team_stats, away_team_stats = (
            match_stat.data[home_team.source.id].m,
            match_stat.data[away_team.source.id].m,
        )
        return self.__get_stats(home_team_stats, away_team_stats), self.__get_stats(
            away_team_stats, home_team_stats
        )

    def __get_stats(
        self,
        stats_our: list[PulseliveMatchStatItemResponse],
        stats_oppo: list[PulseliveMatchStatItemResponse],
    ) -> MatchStatEntity:
        get_our_int = lambda name: self.__get_int_stat(stats_our, name)
        get_oppo_int = lambda name: self.__get_int_stat(stats_oppo, name)
        get_our_float = lambda name: self.__get_float_stat(stats_our, name)
        get_oppo_float = lambda name: self.__get_float_stat(stats_oppo, name)
        big_chance_missed = get_our_int("big_chance_missed")
        aerial_won = get_our_int("aerial_won")
        aerial_total = aerial_won + get_our_int("aerial_lost")
        duel_won = get_our_int("duel_won")
        duel_total = duel_won + get_our_int("duel_lost")
        expected_goals = get_our_float("expected_goals")
        return MatchStatEntity(
            big_chances=get_our_int("big_chance_scored") + big_chance_missed,
            big_chances_missed=big_chance_missed,
            corners=get_our_int("corner_taken"),
            defense_blocks=get_our_int("outfielder_block"),
            defense_clearances=get_our_int("total_clearance"),
            defense_interceptions=get_our_int("interception"),
            defense_keeper_saves=get_our_int("saves"),
            defense_tackles_total=get_our_int("total_tackle"),
            defense_tackles_won=get_our_int("won_tackle"),
            discipline_red_cards=get_our_int("total_red_card"),
            discipline_yellow_cards=get_our_int("total_yel_card"),
            duels_aerial_total=aerial_total,
            duels_aerial_won=aerial_won,
            duels_dribbles_successful=get_our_int("won_contest"),
            duels_dribbles_total=get_our_int("total_contest"),
            duels_ground_total=duel_total - aerial_total,
            duels_ground_won=duel_won - aerial_won,
            duels_total=duel_total,
            duels_won=duel_won,
            expected_goals=expected_goals,
            expected_goals_non_penalty=expected_goals
            - get_oppo_float("penalty_faced") * 0.79,
            expected_goals_on_target=get_our_float("expected_goals_on_target"),
            fouls_committed=get_our_int("fk_foul_lost"),
            passes_accurate=get_our_int("accurate_pass"),
            passes_accurate_crosses=get_our_int("accurate_crosses"),
            passes_accurate_long_balls=get_our_int(""),
        )

    @staticmethod
    def __get_int_stat(stats: list[PulseliveMatchStatItemResponse], name: str) -> int:
        return next(filter(lambda m: m.name == name, stats), 0)

    @staticmethod
    def __get_float_stat(
        stats: list[PulseliveMatchStatItemResponse], name: str
    ) -> float:
        return next(filter(lambda m: m.name == name, stats), 0.0)
