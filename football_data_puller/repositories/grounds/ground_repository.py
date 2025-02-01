from football_data_puller.repositories.base_repository import BaseRepository
from football_data_puller.repositories.grounds.ground_entity import GroundEntity
from football_data_puller.services.db.db_service import DbService


class GroundRepository(BaseRepository[GroundEntity, str]):
    """
    Ground repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, GroundEntity)
