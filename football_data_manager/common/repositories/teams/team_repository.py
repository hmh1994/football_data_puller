from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.db.db_service import DbService


class TeamRepository(BaseRepository[TeamEntity, str]):
    """
    Team repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, TeamEntity)
