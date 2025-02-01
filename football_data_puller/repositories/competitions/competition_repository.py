from football_data_puller.repositories.base_repository import BaseRepository
from football_data_puller.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_puller.services.db.db_service import DbService


class CompetitionRepository(BaseRepository[CompetitionEntity, str]):
    """
    Competition repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, CompetitionEntity)
