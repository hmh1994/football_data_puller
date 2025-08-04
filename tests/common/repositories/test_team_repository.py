from pytest import mark
from sqlalchemy.orm import DeclarativeBase

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from tests.common.repositories.abstract_test_repository import AbstractTestRepository
from tests.common.repositories.sample_data.ground_sample_data import GroundSampleData
from tests.common.repositories.sample_data.team_sample_data import TeamSampleData


class TestTeamRepository(AbstractTestRepository[TeamRepository, TeamEntity]):
    """
    Test cases for TeamRepository class.
    """

    __test__ = True

    @property
    def base(self) -> DeclarativeBase:
        return Base

    @property
    def sample_data(self) -> TeamSampleData:
        return TeamSampleData()

    @mark.asyncio
    async def test_ground_field(
        self, db_service: DbService, repository: TeamRepository
    ):
        """
        Tests the ground field of the team entity.
        :param db_service: Pytest database service fixture.
        :param repository: Team repository instance.
        """
        await self.sample_data.initialize(db_service, add_entity=True)
        fetched_entities = await repository.read_all()
        ground_ids = [entity.id for entity in GroundSampleData().entity_list]
        for entity in fetched_entities:
            print(entity.ground_id, entity.ground)
            assert entity.ground is not None, "Ground field is None."
            assert (
                entity.ground.id in ground_ids
            ), f"Ground ID not found: {entity.ground.id}."
