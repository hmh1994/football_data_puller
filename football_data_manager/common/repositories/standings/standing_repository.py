from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.standings.standing_entity import (
    StandingEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class StandingRepository(BaseRepository[StandingEntity, str]):
    """
    Standing repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, StandingEntity)
