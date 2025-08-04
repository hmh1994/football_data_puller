from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class CompetitionRepository(PulseliveRepository[CompetitionEntity]):
    """
    Repository for managing competition entities.
    
    Provides specialized functionality for handling football competitions and tournaments
    with multilingual support. Extends PulseliveRepository to inherit source-specific operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the competition repository.
        
        :param db_service: Database service for database operations
        """
        super().__init__(db_service, CompetitionEntity)
