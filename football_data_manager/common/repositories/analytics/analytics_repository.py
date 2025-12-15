from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.enums.analytics_key_enum import AnalyticsKeyEnum
from football_data_manager.common.repositories.analytics.analytics_entity import (
    AnalyticsEntity,
)
from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.services.db.db_service import DbService


class AnalyticsRepository(BaseRepository[AnalyticsEntity]):
    """
    Repository for analytics entities.

    Provides CRUD operations and upsert functionality for analytics metrics.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, AnalyticsEntity)

    @BaseRepository.with_db_session
    async def read_by_season_and_key(
        self,
        session: AsyncSession,
        season: SeasonEntity,
        key: AnalyticsKeyEnum,
    ) -> AnalyticsEntity | None:
        """
        Read analytics entity by season and key.

        :param session: Database session
        :param season: Season entity
        :param key: Analytics key enum
        :returns: Analytics entity or None if not found
        """
        stmt = select(AnalyticsEntity).where(
            AnalyticsEntity.season_id == season.id,
            AnalyticsEntity.key == key,
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    @BaseRepository.with_db_session
    async def read_by_season(
        self,
        session: AsyncSession,
        season: SeasonEntity,
    ) -> list[AnalyticsEntity]:
        """
        Read all analytics entities for a season.

        :param session: Database session
        :param season: Season entity
        :returns: List of analytics entities
        """
        stmt = select(AnalyticsEntity).where(
            AnalyticsEntity.season_id == season.id,
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def upsert(
        self,
        analytics_entity: AnalyticsEntity,
    ) -> AnalyticsEntity:
        """
        Create or update an analytics entity.

        Checks if analytics already exists for the given source_id.
        If exists, updates value, delta, title_en, title_kr, description_en, and description_kr.
        If not exists, creates new entity.

        :param analytics_entity: Analytics entity to create or update
        :returns: Created or updated analytics entity
        """
        existing = await self.read_by_source_id(
            analytics_entity.source, analytics_entity.source_id
        )

        if existing:
            existing.title_en = analytics_entity.title_en
            existing.title_kr = analytics_entity.title_kr
            existing.value = analytics_entity.value
            existing.delta = analytics_entity.delta
            existing.description_en = analytics_entity.description_en
            existing.description_kr = analytics_entity.description_kr
            return await self.update(existing)
        else:
            return await self.create(analytics_entity)