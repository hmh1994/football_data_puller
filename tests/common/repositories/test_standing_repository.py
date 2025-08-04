from football_data_manager.common.repositories.standings.standing_entity import (
    StandingEntity,
)
from football_data_manager.common.repositories.standings.standing_repository import (
    StandingRepository,
)
from pytest import mark
from sqlalchemy.orm import DeclarativeBase

from football_data_manager.common.repositories import Base
from football_data_manager.common.services.db.db_service import DbService
from tests.common.repositories.abstract_test_repository import AbstractTestRepository
from tests.common.repositories.sample_data.season_sample_data import SeasonSampleData
from tests.common.repositories.sample_data.standing_sample_data import (
    StandingSampleData,
)
from tests.common.repositories.sample_data.team_sample_data import TeamSampleData


class TestStandingRepository(
    AbstractTestRepository[StandingRepository, StandingEntity]
):
    """
    Test cases for StandingRepository class.
    """

    __test__ = True

    @property
    def base(self) -> DeclarativeBase:
        return Base

    @property
    def sample_data(self) -> StandingSampleData:
        return StandingSampleData()

    @mark.asyncio
    async def test_season_field(
        self, db_service: DbService, repository: StandingRepository
    ):
        """
        Tests the season field of the standing entity.
        :param db_service: Pytest database service fixture.
        :param repository: Standing repository instance.
        """
        await self.sample_data.initialize(db_service, add_entity=True)
        fetched_entities = await repository.read_all()
        season_ids = [entity.id for entity in SeasonSampleData().entity_list]
        for entity in fetched_entities:
            assert entity.season is not None, "Season field is None."
            assert (
                entity.season.id in season_ids
            ), f"Season ID not found: {entity.season.id}."

    @mark.asyncio
    async def test_team_field(
        self, db_service: DbService, repository: StandingRepository
    ):
        """
        Tests the team field of the standing entity.
        :param db_service: Pytest database service fixture.
        :param repository: Standing repository instance.
        """
        await self.sample_data.initialize(db_service, add_entity=True)
        fetched_entities = await repository.read_all()
        team_ids = [entity.id for entity in TeamSampleData().entity_list]
        for entity in fetched_entities:
            assert entity.team is not None, "Team field is None."
            assert entity.team.id in team_ids, f"Team ID not found: {entity.team.id}."
