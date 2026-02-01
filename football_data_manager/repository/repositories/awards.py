from football_data_manager.repository.entities.awards import AwardEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class AwardRepository(PulseliveRepository[AwardEntity]):
    """Repository for award entities with multilingual support."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, AwardEntity)

    async def get_award_name_kr(self, name_en: str) -> str | None:
        """
        Get the Korean name of an award by its English name.

        :param name_en: The English name of the award
        :returns: The Korean name of the award, or None if not found
        """
        result = await self._get_one_by_field(name_en=name_en)
        return result.name_kr if result else None

    async def get_award_description(
        self, name_en: str
    ) -> tuple[str, str] | None:
        """
        Get the descriptions of an award by its English name.

        :param name_en: The English name of the award
        :returns: A tuple of (English description, Korean description), or None
        """
        result = await self._get_one_by_field(name_en=name_en)
        if result is None:
            return None
        if result.description_en is None or result.description_kr is None:
            return None
        return (result.description_en, result.description_kr)

    async def get_icon_url(self, name_en: str) -> str | None:
        """
        Get the icon URL of an award by its English name.

        :param name_en: The English name of the award
        :returns: The icon URL of the award, or None if not found
        """
        result = await self._get_one_by_field(name_en=name_en)
        return result.icon_url if result else None
