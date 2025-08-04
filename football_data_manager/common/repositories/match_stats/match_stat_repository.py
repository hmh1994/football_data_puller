from football_data_manager.common.repositories.match_stats.match_stat_entity import (
    MatchStatEntity,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class MatchStatRepository(PulseliveRepository[MatchStatEntity]):
    """
    Repository for managing match stat entities.
    
    Provides specialized functionality for handling comprehensive match statistics
    including team performance metrics, analytical queries, and statistical aggregations.
    Extends PulseliveRepository to inherit source-specific operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the match stat repository.
        
        :param db_service: Database service for database operations
        """
        super().__init__(db_service, MatchStatEntity)
