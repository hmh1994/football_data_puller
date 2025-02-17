from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.grounds.ground_entity import GroundEntity
from football_data_manager.common.services.db.db_service import DbService


class GroundRepository(BaseRepository[GroundEntity, str]):
    """
    Ground repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, GroundEntity)
