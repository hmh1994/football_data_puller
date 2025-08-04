from pytest import mark
from sqlalchemy.orm import DeclarativeBase

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.repositories.fixtures.fixture_repository import (
    FixtureRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from tests.common.repositories.abstract_test_repository import AbstractTestRepository
from tests.common.repositories.sample_data.fixture_sample_data import FixtureSampleData
from tests.common.repositories.sample_data.ground_sample_data import GroundSampleData
from tests.common.repositories.sample_data.season_sample_data import SeasonSampleData
from tests.common.repositories.sample_data.team_sample_data import TeamSampleData


class TestFixtureRepository(AbstractTestRepository[FixtureRepository, FixtureEntity]):
    """
    Test cases for FixtureRepository class.
    """

    __test__ = True

    @property
    def base(self) -> DeclarativeBase:
        return Base

    @property
    def sample_data(self) -> FixtureSampleData:
        return FixtureSampleData()

    @mark.asyncio
    async def test_home_team_field(
        self, db_service: DbService, repository: FixtureRepository
    ):
        """
        Tests the home team field of the fixture entity.
        :param db_service: Pytest database service fixture.
        :param repository: Fixture repository instance.
        """
        await self.sample_data.initialize(db_service, add_entity=True)
        fetched_entities = await repository.read_all()
        team_ids = [entity.id for entity in TeamSampleData().entity_list]
        for entity in fetched_entities:
            assert entity.home_team is not None, "Home team field is None."
            assert (
                entity.home_team.id in team_ids
            ), f"Home team ID not found: {entity.home_team.id}."

    @mark.asyncio
    async def test_away_team_field(
        self, db_service: DbService, repository: FixtureRepository
    ):
        """
        Tests the away team field of the fixture entity.
        :param db_service: Pytest database service fixture.
        :param repository: Fixture repository instance.
        """
        await self.sample_data.initialize(db_service, add_entity=True)
        fetched_entities = await repository.read_all()
        team_ids = [entity.id for entity in TeamSampleData().entity_list]
        for entity in fetched_entities:
            assert entity.away_team is not None, "Away team field is None."
            assert (
                entity.away_team.id in team_ids
            ), f"Away team ID not found: {entity.away_team.id}."

    @mark.asyncio
    async def test_ground_field(
        self, db_service: DbService, repository: FixtureRepository
    ):
        """
        Tests the ground field of the fixture entity.
        :param db_service: Pytest database service fixture.
        :param repository: Fixture repository instance.
        """
        await self.sample_data.initialize(db_service, add_entity=True)
        fetched_entities = await repository.read_all()
        ground_ids = [entity.id for entity in GroundSampleData().entity_list]
        for entity in fetched_entities:
            assert entity.ground is not None, "Ground field is None."
            assert (
                entity.ground.id in ground_ids
            ), f"Ground ID not found: {entity.ground.id}."

    @mark.asyncio
    async def test_season_field(
        self, db_service: DbService, repository: FixtureRepository
    ):
        """
        Tests the season field of the fixture entity.
        :param db_service: Pytest database service fixture.
        :param repository: Fixture repository instance.
        """
        await self.sample_data.initialize(db_service, add_entity=True)
        fetched_entities = await repository.read_all()
        season_ids = [entity.id for entity in SeasonSampleData().entity_list]
        for entity in fetched_entities:
            assert entity.season is not None, "Season field is None."
            assert (
                entity.season.id in season_ids
            ), f"Season ID not found: {entity.season.id}."
