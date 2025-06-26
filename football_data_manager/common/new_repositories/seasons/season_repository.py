from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class SeasonRepository(BaseRepository[SeasonEntity]):
    """
    Season repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, SeasonEntity)
