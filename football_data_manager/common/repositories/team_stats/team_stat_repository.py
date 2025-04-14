from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class TeamStatRepository(BaseRepository[TeamStatEntity, str]):
    """
    Team statistics repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, TeamStatEntity)
