from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.repositories.staffs.staff_entity import (
    StaffEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class StaffRepository(PulseliveRepository[StaffEntity]):
    """
    Repository for managing staff entities with multilingual name support.
    
    Provides specialized functionality for football coaching staff and management personnel
    including display name lookups in multiple languages and full name searches.
    Extends PulseliveRepository for standard PULSELIVE source operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the staff repository.
        
        :param db_service: Database service for database operations
        """
        super().__init__(db_service, StaffEntity)
        
    async def read_by_display_name_en(self, name: str) -> StaffEntity | None:
        """
        Read a staff entity by their English display name.
        
        Searches for a staff member using their English display name which serves
        as a unique identifier in the system.
        
        :param name: The English display name of the staff member
        :returns: The staff entity if found, otherwise None
        """
        return await self._read_one_by_field(display_name_en=name)
        
    async def read_by_full_name(self, name: str) -> StaffEntity | None:
        """
        Read a staff entity by their full legal name.
        
        Searches for a staff member using their complete legal name as recorded
        in the system.
        
        :param name: The full legal name of the staff member
        :returns: The staff entity if found, otherwise None
        """
        return await self._read_one_by_field(full_name=name)
