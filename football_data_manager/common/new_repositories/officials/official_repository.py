from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.officials.official_entity import (
    OfficialEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class OfficialRepository(BaseRepository[OfficialEntity]):
    """ """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, OfficialEntity)

    async def read_by_display_name_en(self, name: str) -> OfficialEntity | None:
        """
        Read an official by their English display name.
        :param name: The English display name of the official.
        :return: An OfficialEntity object if found, otherwise None.
        """
        return await self._read_one_by_field(display_name_en=name)
