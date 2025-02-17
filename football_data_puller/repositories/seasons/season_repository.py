from football_data_puller.repositories.base_repository import BaseRepository
from football_data_puller.repositories.seasons.season_entity import SeasonEntity
from football_data_puller.services.db.db_service import DbService


class SeasonRepository(BaseRepository[SeasonEntity, str]):
    """
    Season repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, SeasonEntity)
