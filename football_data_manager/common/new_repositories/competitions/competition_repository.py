from football_data_manager.common.new_repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.new_repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class CompetitionRepository(PulseliveRepository[CompetitionEntity]):
    """
    Competition repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, CompetitionEntity)
