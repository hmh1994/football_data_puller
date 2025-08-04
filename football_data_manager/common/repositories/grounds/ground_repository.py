from football_data_manager.common.repositories.grounds.ground_entity import (
    GroundEntity,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class GroundRepository(PulseliveRepository[GroundEntity]):
    """
    Repository for managing ground entities.
    
    Provides specialized functionality for handling football grounds (stadiums/venues)
    with location-based queries and capacity management. Extends PulseliveRepository to inherit source-specific operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the ground repository.
        
        :param db_service: Database service for database operations
        """
        super().__init__(db_service, GroundEntity)
