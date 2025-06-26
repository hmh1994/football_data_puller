from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class PlayerRepository(BaseRepository[PlayerEntity]):
    """
    Player repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, PlayerEntity)

    @BaseRepository.with_db_session
    async def get_birth_country_kr(
        self, session: AsyncSession, birth_country_en: str
    ) -> str:
        """
        Get the Korean name of a player's birth country by its English name.
        :param session: The database session.
        :param birth_country_en: The English name of the birth country.
        :return: The Korean name of the birth country, or None if not found.
        """
        stmt = (
            select(self.model)
            .where(self.model.birth_country_en == birth_country_en)
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalars().first().birth_country_kr if result else None

    @BaseRepository.with_db_session
    async def get_position_info_kr(
        self, session: AsyncSession, position_info_en: str
    ) -> str:
        """
        Get the Korean name of a player's position by its English name.
        :param session: The database session.
        :param position_info_en: The English name of the position.
        :return: The Korean name of the position, or None if not found.
        """
        stmt = (
            select(self.model)
            .where(self.model.position_info_en == position_info_en)
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalars().first().position_info_kr if result else None
