from typing import TypeVar

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.repository.entities.base import PulseliveEntity
from football_data_manager.repository.repositories.base import AsyncBaseRepository

TEntity = TypeVar("TEntity", bound=PulseliveEntity)


class PulseliveRepository(AsyncBaseRepository[TEntity]):
    """Repository for Pulselive-sourced entities."""

    async def exists_by_pulselive_id(self, source_id: str) -> bool:
        """Check existence by Pulselive source ID."""
        return await self.exists_by_source(SourceEnum.PULSELIVE, source_id)

    async def get_by_pulselive_id(self, source_id: str) -> TEntity | None:
        """Get entity by Pulselive source ID."""
        return await self.get_by_source(SourceEnum.PULSELIVE, source_id)
