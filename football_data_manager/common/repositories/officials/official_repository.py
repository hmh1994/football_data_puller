from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.officials.official_entity import (
    OfficialEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class OfficialRepository(BaseRepository[OfficialEntity]):
    """
    Repository for managing official entities.
    
    Provides specialized functionality for handling football officials (referees, assistants, VAR officials)
    with multilingual name support and display name lookups. Extends BaseRepository for standard operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the official repository.
        
        :param db_service: Database service for database operations
        """
        super().__init__(db_service, OfficialEntity)

    async def read_by_display_name_en(self, name: str) -> OfficialEntity | None:
        """
        Read an official by their English display name.
        
        Searches for an official using their English display name which serves
        as a unique identifier in the system.
        
        :param name: The English display name of the official
        :returns: An OfficialEntity object if found, otherwise None
        """
        return await self._read_one_by_field(display_name_en=name)
