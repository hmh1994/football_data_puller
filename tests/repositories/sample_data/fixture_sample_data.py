from football_data_puller.repositories.fixtures.fixture_entity import FixtureEntity
from football_data_puller.repositories.fixtures.fixture_repository import (
    FixtureRepository,
)
from football_data_puller.services.db.db_service import DbService
from football_data_puller.utils.type_helper.datetime_helper import (
    create_utc_datetime,
    TimeZone,
)
from tests.repositories.sample_data.abstract_sample_data import AbstractSampleData
from tests.repositories.sample_data.ground_sample_data import GroundSampleData
from tests.repositories.sample_data.season_sample_data import SeasonSampleData
from tests.repositories.sample_data.team_sample_data import TeamSampleData
from tests.utils.random import random_string


class FixtureSampleData(AbstractSampleData[FixtureRepository, FixtureEntity, str]):
    """
    Fixture sample data.
    """

    @property
    def prerequisites(self) -> list[type[AbstractSampleData]]:
        return [GroundSampleData, SeasonSampleData, TeamSampleData]

    @property
    def entity_list(self) -> list[FixtureEntity]:
        return [
            FixtureEntity(
                id="PULSELIVE_FIXTURE_12272",
                away_team_id="PULSELIVE_TEAM_12",
                away_team_score=1,
                attendance=60192,
                clock=6180,
                game_week=4,
                ground_id="PULSELIVE_GROUND_52",
                home_team_id="PULSELIVE_TEAM_1",
                home_team_score=3,
                neutral_ground=False,
                kickoff_time=create_utc_datetime(
                    2023,
                    9,
                    3,
                    16,
                    30,
                    timezone=TimeZone.BST,
                ),
                season_id="PULSELIVE_SEASON_578",
            ),
            FixtureEntity(
                id="PULSELIVE_FIXTURE_12285",
                away_team_id="PULSELIVE_TEAM_12",
                away_team_score=0,
                attendance=57158,
                clock=5760,
                game_week=17,
                ground_id="PULSELIVE_GROUND_7305",
                home_team_id="PULSELIVE_TEAM_10",
                home_team_score=0,
                neutral_ground=False,
                kickoff_time=create_utc_datetime(
                    2023,
                    12,
                    17,
                    16,
                    30,
                ),
                season_id="PULSELIVE_SEASON_578",
            ),
            FixtureEntity(
                id="PULSELIVE_FIXTURE_12286",
                away_team_id="PULSELIVE_TEAM_1",
                away_team_score=1,
                attendance=57548,
                clock=5760,
                game_week=18,
                ground_id="PULSELIVE_GROUND_7305",
                home_team_id="PULSELIVE_TEAM_10",
                home_team_score=1,
                neutral_ground=False,
                kickoff_time=create_utc_datetime(
                    2023,
                    12,
                    23,
                    17,
                    30,
                ),
                season_id="PULSELIVE_SEASON_578",
            ),
            FixtureEntity(
                id="PULSELIVE_FIXTURE_12291",
                away_team_id="PULSELIVE_TEAM_10",
                away_team_score=1,
                attendance=60374,
                clock=5880,
                game_week=23,
                ground_id="PULSELIVE_GROUND_52",
                home_team_id="PULSELIVE_TEAM_1",
                home_team_score=3,
                neutral_ground=False,
                kickoff_time=create_utc_datetime(
                    2024,
                    2,
                    4,
                    16,
                    30,
                ),
                season_id="PULSELIVE_SEASON_578",
            ),
            FixtureEntity(
                id="PULSELIVE_FIXTURE_12300",
                away_team_id="PULSELIVE_TEAM_12",
                away_team_score=2,
                attendance=73522,
                clock=5880,
                game_week=32,
                ground_id="PULSELIVE_GROUND_42",
                home_team_id="PULSELIVE_TEAM_10",
                home_team_score=2,
                neutral_ground=False,
                kickoff_time=create_utc_datetime(
                    2024,
                    4,
                    7,
                    15,
                    30,
                    timezone=TimeZone.BST,
                ),
                season_id="PULSELIVE_SEASON_578",
            ),
            FixtureEntity(
                id="PULSELIVE_FIXTURE_12305",
                away_team_id="PULSELIVE_TEAM_1",
                away_team_score=1,
                attendance=73600,
                clock=5820,
                game_week=37,
                ground_id="PULSELIVE_GROUND_42",
                home_team_id="PULSELIVE_TEAM_12",
                home_team_score=0,
                neutral_ground=False,
                kickoff_time=create_utc_datetime(
                    2024,
                    5,
                    12,
                    16,
                    30,
                    timezone=TimeZone.BST,
                ),
                season_id="PULSELIVE_SEASON_578",
            ),
        ]

    @staticmethod
    def repository_instance(db_service: DbService) -> FixtureRepository:
        return FixtureRepository(db_service)

    @staticmethod
    def random_id() -> str:
        return random_string(20)
