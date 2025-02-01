from football_data_puller.repositories.base_repository import BaseRepository
from football_data_puller.repositories.standings.standing_entity import StandingEntity
from football_data_puller.services.db.db_service import DbService


class StandingRepository(BaseRepository[StandingEntity, str]):
    """
    Standing repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, StandingEntity)
