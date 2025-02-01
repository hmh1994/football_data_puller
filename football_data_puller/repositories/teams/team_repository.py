from football_data_puller.repositories.base_repository import BaseRepository
from football_data_puller.repositories.teams.team_entity import TeamEntity
from football_data_puller.services.db.db_service import DbService


class TeamRepository(BaseRepository[TeamEntity, str]):
    """
    Team repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, TeamEntity)
