from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.player_stats.player_stat_entity import (
    PlayerStatEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class PlayerStatRepository(BaseRepository[PlayerStatEntity]):
    """
    Player statistics repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, PlayerStatEntity)
