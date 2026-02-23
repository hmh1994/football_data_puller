from football_data_manager.repository.entities.officials import OfficialEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class OfficialRepository(PulseliveRepository[OfficialEntity]):
    """Repository for official entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, OfficialEntity)

    async def get_by_display_name_en(
        self, display_name_en: str
    ) -> OfficialEntity | None:
        """Get official by English display name."""
        return await self._get_one_by_field(display_name_en=display_name_en)
