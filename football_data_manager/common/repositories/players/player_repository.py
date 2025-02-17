from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.players.player_entity import PlayerEntity
from football_data_manager.common.services.db.db_service import DbService


class PlayerRepository(BaseRepository[PlayerEntity, str]):
    """
    Player repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, PlayerEntity)
