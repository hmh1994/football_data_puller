from football_data_manager.common.new_repositories.standings.standing_entity import (
    StandingEntity,
)
from football_data_manager.common.new_repositories.standings.standing_repository import (
    StandingRepository,
)

from football_data_manager.common.services.db.db_service import DbService
from tests.common.repositories.sample_data.abstract_sample_data import (
    AbstractSampleData,
)
from tests.common.repositories.sample_data.season_sample_data import SeasonSampleData
from tests.common.repositories.sample_data.team_sample_data import TeamSampleData
from tests.common.utils.random import random_string


class StandingSampleData(AbstractSampleData[StandingRepository, StandingEntity, str]):
    """
    Standing sample data.
    """

    @property
    def prerequisites(self) -> list[type[AbstractSampleData]]:
        return [SeasonSampleData, TeamSampleData]

    @property
    def entity_list(self) -> list[StandingEntity]:
        return [
            StandingEntity(
                id="PULSELIVE_STANDING_578_38_1",
                away_matches=19,
                away_matches_drawn=3,
                away_matches_lost=3,
                away_matches_won=13,
                away_goals_against=13,
                away_goals_for=43,
                away_goal_difference=30,
                away_points=42,
                away_positions=2,
                game_week=38,
                home_matches=19,
                home_matches_drawn=2,
                home_matches_lost=2,
                home_matches_won=15,
                home_goals_against=16,
                home_goals_for=48,
                home_goal_difference=32,
                home_points=47,
                home_positions=3,
                latest=True,
                last_five_matches="WWWWW",
                overall_matches=38,
                overall_matches_drawn=5,
                overall_matches_lost=5,
                overall_matches_won=28,
                overall_goals_against=29,
                overall_goals_for=91,
                overall_goal_difference=62,
                overall_points=89,
                overall_position=2,
                season_id="PULSELIVE_SEASON_578",
                team_id="PULSELIVE_TEAM_1",
            ),
            StandingEntity(
                id="PULSELIVE_STANDING_578_38_10",
                away_matches=19,
                away_matches_drawn=7,
                away_matches_lost=3,
                away_matches_won=9,
                away_goals_against=24,
                away_goals_for=37,
                away_goal_difference=13,
                away_points=34,
                away_positions=3,
                game_week=38,
                home_matches=19,
                home_matches_drawn=3,
                home_matches_lost=1,
                home_matches_won=15,
                home_goals_against=17,
                home_goals_for=49,
                home_goal_difference=32,
                home_points=48,
                home_positions=1,
                latest=True,
                last_five_matches="LDWDW",
                overall_matches=38,
                overall_matches_drawn=10,
                overall_matches_lost=4,
                overall_matches_won=24,
                overall_goals_against=41,
                overall_goals_for=86,
                overall_goal_difference=45,
                overall_points=82,
                overall_position=3,
                season_id="PULSELIVE_SEASON_578",
                team_id="PULSELIVE_TEAM_10",
            ),
            StandingEntity(
                id="PULSELIVE_STANDING_578_38_12",
                away_matches=19,
                away_matches_drawn=3,
                away_matches_lost=8,
                away_matches_won=8,
                away_goals_against=30,
                away_goals_for=26,
                away_goal_difference=-4,
                away_points=27,
                away_positions=6,
                game_week=38,
                home_matches=19,
                home_matches_drawn=3,
                home_matches_lost=6,
                home_matches_won=10,
                home_goals_against=28,
                home_goals_for=31,
                home_goal_difference=3,
                home_points=33,
                home_positions=8,
                latest=True,
                last_five_matches="DLLWW",
                overall_matches=38,
                overall_matches_drawn=6,
                overall_matches_lost=14,
                overall_matches_won=18,
                overall_goals_against=58,
                overall_goals_for=57,
                overall_goal_difference=-1,
                overall_points=60,
                overall_position=8,
                season_id="PULSELIVE_SEASON_578",
                team_id="PULSELIVE_TEAM_12",
            ),
        ]

    @staticmethod
    def repository_instance(db_service: DbService) -> StandingRepository:
        return StandingRepository(db_service)

    @staticmethod
    def random_id() -> str:
        return random_string(20)
