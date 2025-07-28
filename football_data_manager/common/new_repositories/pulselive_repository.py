from typing import TypeVar

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.pulselive_entity import (
    PulseliveEntity,
)

TEntity = TypeVar("TEntity", bound=PulseliveEntity)


class PulseliveRepository(BaseRepository[TEntity]):

    async def read_by_pulselive_id(self, source_id: str) -> TEntity:
        """
        Reads an entity by Pulselive ID from the database.
        :param source_id: Pulselive ID.
        :return: An entity or None if not found.
        """
        return await self.read_by_source_id(SourceEnum.PULSELIVE, source_id)
