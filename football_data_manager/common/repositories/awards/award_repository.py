from football_data_manager.common.repositories.awards.award_entity import (
    AwardEntity,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class AwardRepository(PulseliveRepository[AwardEntity]):
    """
    Repository for managing award entities.
    
    Provides specialized functionality for handling football awards and achievements
    with multilingual support. Extends PulseliveRepository to inherit source-specific operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the award repository.
        
        :param db_service: Database service for database operations
        """
        super().__init__(db_service, AwardEntity)

    async def get_award_name_kr(self, name_en: str) -> str | None:
        """
        Get the Korean name of an award by its English name.
        
        :param name_en: The English name of the award
        :returns: The Korean name of the award, or None if not found
        """
        result = await self._read_one_by_field(name_en=name_en)
        return result.name_kr if result else None

    async def get_award_description(self, name_en: str) -> tuple[str, str] | None:
        """
        Get the descriptions of an award by its English name.
        
        :param name_en: The English name of the award
        :returns: A tuple containing (English description, Korean description), or None if not found
        """
        result = await self._read_one_by_field(name_en=name_en)
        if result.description_en is None or result.description_kr is None:
            return None
        else:
            return (result.description_en, result.description_kr) if result else None

    async def get_icon_url(self, name_en: str) -> str | None:
        """
        Get the icon URL of an award by its English name.
        
        :param name_en: The English name of the award
        :returns: The icon URL of the award, or None if not found
        """
        result = await self._read_one_by_field(name_en=name_en)
        return result.icon_url if result else None
