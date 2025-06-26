from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.new_repositories.awards.award_entity import (
    AwardEntity,
)
from football_data_manager.common.new_repositories.base_repository import BaseRepository


class AwardRepository(BaseRepository[AwardEntity]):
    """
    Award repository.
    """

    def __init__(self, db_service):
        super().__init__(db_service, AwardEntity)

    @BaseRepository.with_db_session
    async def get_award_name_kr(
        self, session: AsyncSession, name_en: str
    ) -> str | None:
        """
        Get the Korean name of an award by its English name.
        :param session: The database session.
        :param name_en: The English name of the award.
        :return: The Korean name of the award, or None if not found.
        """
        stmt = select(self.model).where(self.model.name_en == name_en).limit(1)
        result = await session.execute(stmt)
        return result.scalars().first().name_kr if result else None

    @BaseRepository.with_db_session
    async def get_award_description(
        self, session: AsyncSession, name_en: str
    ) -> tuple[str, str] | None:
        """
        Get the descriptions of an award by its English name.
        :param session: The database session.
        :param name_en: The English name of the award.
        :return: A tuple containing the English and Korean descriptions of the award, or None if not found.
        """
        stmt = select(self.model).where(self.model.name_en == name_en).limit(1)
        result = await session.execute(stmt)
        if result is None:
            return None
        else:
            entity = result.scalars().first()
            return entity.description_en, entity.description_kr

    @BaseRepository.with_db_session
    async def get_icon_url(self, session: AsyncSession, name_en: str) -> str | None:
        """
        Get the icon URL of an award by its English name.
        :param session: The database session.
        :param name_en: The English name of the award.
        :return: The icon URL of the award, or None if not found.
        """
        stmt = select(self.model).where(self.model.name_en == name_en).limit(1)
        result = await session.execute(stmt)
        return result.scalars().first().icon_url if result else None
