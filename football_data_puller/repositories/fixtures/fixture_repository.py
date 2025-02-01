from football_data_puller.repositories.base_repository import BaseRepository
from football_data_puller.repositories.fixtures.fixture_entity import FixtureEntity
from football_data_puller.services.db.db_service import DbService


class FixtureRepository(BaseRepository[FixtureEntity, str]):
    """
    Fixture repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, FixtureEntity)
