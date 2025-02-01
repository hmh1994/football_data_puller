from football_data_puller.repositories.base_repository import BaseRepository
from football_data_puller.repositories.players.player_entity import PlayerEntity
from football_data_puller.services.db.db_service import DbService


class PlayerRepository(BaseRepository[PlayerEntity, str]):
    """
    Player repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, PlayerEntity)
