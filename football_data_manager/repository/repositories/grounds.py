from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class GroundRepository(PulseliveRepository[GroundEntity]):
    """Repository for ground entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, GroundEntity)

    async def get_by_name_en(self, name_en: str) -> GroundEntity | None:
        """Get ground by English name."""
        return await self._get_one_by_field(name_en=name_en)
