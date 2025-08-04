from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class SeasonRepository(PulseliveRepository[SeasonEntity]):
    """
    Repository for managing season entities with competition associations.
    
    Provides specialized functionality for football seasons including temporal queries,
    competition-based filtering, and year-based season lookups.
    Extends PulseliveRepository for standard PULSELIVE source operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the season repository.
        
        :param db_service: Database service for database operations
        """
        super().__init__(db_service, SeasonEntity)
