from football_data_manager.common.old_repositories.base_repository import BaseRepository
from football_data_manager.common.old_repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class CompetitionRepository(BaseRepository[CompetitionEntity, str]):
    """
    Competition repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, CompetitionEntity)
