from pytest import mark
from sqlalchemy.orm import DeclarativeBase

from football_data_manager.common.old_repositories import Base
from football_data_manager.common.old_repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.old_repositories.players.player_repository import (
    PlayerRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from tests.common.repositories.abstract_test_repository import AbstractTestRepository
from tests.common.repositories.sample_data.player_sample_data import PlayerSampleData
from tests.common.repositories.sample_data.team_sample_data import TeamSampleData


class TestPlayerRepository(AbstractTestRepository[PlayerRepository, PlayerEntity]):
    """
    Test cases for PlayerRepository class.
    """

    __test__ = True

    @property
    def base(self) -> DeclarativeBase:
        return Base

    @property
    def sample_data(self) -> PlayerSampleData:
        return PlayerSampleData()

    @mark.asyncio
    async def test_team_field(
        self, db_service: DbService, repository: PlayerRepository
    ):
        """
        Tests the team field of the player entity.
        :param db_service: Pytest database service fixture.
        :param repository: Player repository instance.
        """
        await self.sample_data.initialize(db_service, add_entity=True)
        fetched_entities = await repository.read_all()
        team_ids = [entity.id for entity in TeamSampleData().entity_list]
        for entity in fetched_entities:
            assert entity.current_team is not None, "Team field is None."
            assert (
                entity.current_team.id in team_ids
            ), f"Team ID not found: {entity.current_team.id}."
