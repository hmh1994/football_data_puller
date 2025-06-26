from football_data_manager.common.old_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.old_repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_datetime,
    TimeZone,
)
from tests.common.repositories.sample_data.abstract_sample_data import (
    AbstractSampleData,
)
from tests.common.repositories.sample_data.competition_sample_data import (
    CompetitionSampleData,
)
from tests.common.utils.random import random_string


class SeasonSampleData(AbstractSampleData[SeasonRepository, SeasonEntity, str]):
    """
    Season sample data.
    """

    @property
    def prerequisites(self) -> list[type[AbstractSampleData]]:
        return [CompetitionSampleData]

    @property
    def entity_list(self) -> list[SeasonEntity]:
        return [
            SeasonEntity(
                id="PULSELIVE_SEASON_578",
                abbreviation="23/24",
                competition_id="PULSELIVE_COMPETITION_1",
                date_end=create_utc_datetime(
                    2024,
                    5,
                    19,
                    16,
                    0,
                    timezone=TimeZone.BST,
                ),
                date_start=create_utc_datetime(
                    2023,
                    8,
                    11,
                    20,
                    0,
                    timezone=TimeZone.BST,
                ),
                year_end=2024,
                year_start=2023,
            ),
            SeasonEntity(
                id="PULSELIVE_SEASON_589",
                abbreviation="23/24",
                competition_id="PULSELIVE_COMPETITION_2",
                date_end=create_utc_datetime(2024, 6, 1, 20, 0),
                date_start=create_utc_datetime(
                    2023,
                    9,
                    19,
                    17,
                    45,
                    timezone=TimeZone.BST,
                ),
                year_end=2024,
                year_start=2023,
            ),
            SeasonEntity(
                id="PULSELIVE_SEASON_676",
                abbreviation="23/24",
                competition_id="PULSELIVE_COMPETITION_3",
                date_end=create_utc_datetime(
                    2024,
                    5,
                    22,
                    20,
                    0,
                    timezone=TimeZone.BST,
                ),
                date_start=create_utc_datetime(
                    2023,
                    9,
                    21,
                    17,
                    45,
                    timezone=TimeZone.BST,
                ),
                year_end=2024,
                year_start=2023,
            ),
            SeasonEntity(
                id="PULSELIVE_SEASON_690",
                abbreviation="23/24",
                competition_id="PULSELIVE_COMPETITION_2247",
                date_end=create_utc_datetime(
                    2024,
                    5,
                    29,
                    20,
                    0,
                    timezone=TimeZone.BST,
                ),
                date_start=create_utc_datetime(
                    2023,
                    9,
                    20,
                    15,
                    30,
                    timezone=TimeZone.BST,
                ),
                year_end=2024,
                year_start=2023,
            ),
            SeasonEntity(
                id="PULSELIVE_SEASON_700",
                abbreviation="23/24",
                competition_id="PULSELIVE_COMPETITION_4",
                date_end=create_utc_datetime(
                    2024,
                    5,
                    25,
                    15,
                    0,
                    timezone=TimeZone.UTC,
                ),
                date_start=create_utc_datetime(
                    2023,
                    11,
                    3,
                    19,
                    45,
                    timezone=TimeZone.BST,
                ),
                year_end=2024,
                year_start=2023,
            ),
        ]

    @staticmethod
    def repository_instance(db_service: DbService) -> SeasonRepository:
        return SeasonRepository(db_service)

    @staticmethod
    def random_id() -> str:
        return random_string(20)
