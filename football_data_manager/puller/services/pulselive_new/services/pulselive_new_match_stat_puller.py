
from football_data_manager.common.repositories.match_stats.match_stat_entity import (
    MatchStatEntity,
)
from football_data_manager.common.repositories.match_stats.match_stat_repository import (
    MatchStatRepository,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.puller.services.pulselive_new.components.pulselive_new_webclient import (
    PulseliveNewWebclient,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_match_stat_info_response import (
    PulseliveNewMatchStatInfoResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_match_team_stat_response import (
    PulseliveNewV1MatchTeamStatResponse,
)


class PulseliveNewMatchStatPuller:

    __match_stat_repository: MatchStatRepository
    __team_repository: TeamRepository
    __webclient: PulseliveNewWebclient

    def __init__(
        self,
        repository_container: CommonRepositoryContainer,
        pulselive_service: PulseliveNewWebclient,
    ):
        self.__match_stat_repository = repository_container.match_stat_repository()
        self.__team_repository = repository_container.team_repository()
        self.__webclient = pulselive_service

    async def pull_match_stat(self, match: MatchEntity) -> MatchStatEntity:
        match_stat = await self.__webclient.get_v1_match_stat(match.source_id)
        home_match_stat, away_match_stat = await self.__process_match_stat(
            match, match_stat
        )
        return await self.__match_stat_repository.create_all(
            [home_match_stat, away_match_stat]
        )

    async def __process_match_stat(
        self,
        match: MatchEntity,
        match_stat: list[PulseliveNewV1MatchTeamStatResponse],
    ) -> tuple[MatchStatEntity, MatchStatEntity]:
        home_team_stat, away_team_stat = self.__get_each_team_stat(match_stat)
        home_team = await self.__team_repository.read_by_pulselive_id(home_team_stat.team_id)
        away_team = await self.__team_repository.read_by_pulselive_id(away_team_stat.team_id)
        return (
            self.__get_stat(
                match, home_team, home_team_stat.stats, away_team_stat.stats
            ),
            self.__get_stat(
                match, away_team, away_team_stat.stats, home_team_stat.stats
            ),
        )

    @staticmethod
    def __get_each_team_stat(
        match_stat: list[PulseliveNewV1MatchTeamStatResponse],
    ) -> tuple[
        PulseliveNewV1MatchTeamStatResponse, PulseliveNewV1MatchTeamStatResponse
    ]:
        return next(filter(lambda m: m.side == "Home", match_stat)), next(
            filter(lambda m: m.side == "Away", match_stat)
        )

    @staticmethod
    def __get_stat(
        match: MatchEntity,
        team: TeamEntity,
        stats_our: PulseliveNewMatchStatInfoResponse,
        stats_oppo: PulseliveNewMatchStatInfoResponse,
    ) -> MatchStatEntity:
        duels_aerial_total = stats_our.aerial_won + stats_our.aerial_lost
        duels_total = stats_our.duel_won + stats_our.duel_lost
        return MatchStatEntity(
            big_chances=int(stats_our.big_chance_scored + stats_our.big_chance_missed),
            big_chances_missed=int(stats_our.big_chance_missed),
            corners=int(stats_our.corner_taken),
            defense_blocks=int(stats_our.outfielder_block),
            defense_clearances=int(stats_our.total_clearance),
            defense_interceptions=int(stats_our.interception),
            defense_keeper_saves=int(stats_our.saves),
            defense_tackles_total=int(stats_our.total_tackle),
            defense_tackles_won=int(stats_our.won_tackle),
            discipline_red_cards=int(stats_our.total_red_card),
            discipline_yellow_cards=int(stats_our.total_yel_card),
            duels_aerial_total=int(duels_aerial_total),
            duels_aerial_won=int(stats_our.aerial_won),
            duels_dribbles_successful=int(stats_our.won_contest),
            duels_dribbles_total=int(stats_our.total_contest),
            duels_ground_total=int(duels_total - duels_aerial_total),
            duels_ground_won=int(stats_our.duel_won - stats_our.aerial_won),
            duels_total=int(duels_total),
            duels_won=int(stats_our.duel_won),
            expected_goals=stats_our.expected_goals,
            expected_goals_non_penalty=stats_our.expected_goals
            - (stats_oppo.penalty_faced * 0.79),
            expected_goals_on_target=stats_our.expected_goals_on_target,
            fouls_committed=int(stats_our.fk_foul_lost),
            passes_accurate=int(stats_our.accurate_pass),
            passes_accurate_crosses=int(stats_our.accurate_cross),
            passes_accurate_long_balls=int(stats_our.accurate_long_balls),
            passes_offsides=int(stats_our.total_offside),
            passes_opposition_half=int(
                stats_our.accurate_fwd_zone_pass - stats_our.accurate_cross
            ),
            passes_own_half=int(stats_our.accurate_back_zone_pass),
            passes_throws=int(stats_our.total_throws),
            passes_total=int(stats_our.total_pass),
            passes_total_crosses=int(stats_our.total_cross),
            passes_total_long_balls=int(stats_our.total_long_balls),
            passes_touches_in_opposition_box=int(stats_our.touches_in_opp_box),
            possession=stats_our.possession_percentage,
            shots_blocked=int(stats_our.blocked_scoring_att),
            shots_hit_woodwork=int(stats_our.hit_woodwork),
            shots_inside_box=int(stats_our.attempts_ibox),
            shots_off_target=int(stats_our.shot_off_target),
            shots_on_target=int(stats_our.ontarget_scoring_att),
            shots_outside_box=int(stats_our.attempts_obox),
            shots_total=int(stats_our.total_scoring_att),
            match=match,
            team=team,
        )
