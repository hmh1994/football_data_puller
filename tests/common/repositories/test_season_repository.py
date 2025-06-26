from pytest import mark
from sqlalchemy.orm import DeclarativeBase

from football_data_manager.common.old_repositories import Base
from football_data_manager.common.old_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.old_repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from tests.common.repositories.abstract_test_repository import AbstractTestRepository
from tests.common.repositories.sample_data.competition_sample_data import (
    CompetitionSampleData,
)
from tests.common.repositories.sample_data.season_sample_data import SeasonSampleData


class TestSeasonRepository(AbstractTestRepository[SeasonRepository, SeasonEntity]):
    """
    Test cases for SeasonRepository class.
    """

    __test__ = True

    @property
    def base(self) -> DeclarativeBase:
        return Base

    @property
    def sample_data(self) -> SeasonSampleData:
        return SeasonSampleData()

    @mark.asyncio
    async def test_competition_field(
        self, db_service: DbService, repository: SeasonRepository
    ):
        """
        Tests the competition field of the season entity.
        :param db_service: Pytest database service fixture.
        :param repository: Season repository instance.
        """
        await self.sample_data.initialize(db_service, add_entity=True)
        fetched_entities = await repository.read_all()
        competition_ids = [entity.id for entity in CompetitionSampleData().entity_list]
        for entity in fetched_entities:
            assert entity.competition is not None, "Competition field is None."
            assert (
                entity.competition.id in competition_ids
            ), f"Competition ID not found: {entity.competition.id}."
