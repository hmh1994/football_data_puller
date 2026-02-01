from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.enums.analytics_key_enum import AnalyticsKeyEnum
from football_data_manager.repository.entities.analytics import AnalyticsEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.repositories.base import AsyncBaseRepository
from football_data_manager.repository.session import SessionFactory


class AnalyticsRepository(AsyncBaseRepository[AnalyticsEntity]):
    """Repository for analytics entities with season-based queries."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, AnalyticsEntity)

    async def get_by_season_and_key(
        self,
        season: SeasonEntity,
        key: AnalyticsKeyEnum,
        session: AsyncSession | None = None,
    ) -> AnalyticsEntity | None:
        """
        Get analytics entity by season and key.

        :param season: Season entity
        :param key: Analytics metric key
        :param session: Optional existing session
        :return: Analytics entity or None
        """
        async def _do(s: AsyncSession) -> AnalyticsEntity | None:
            stmt = select(AnalyticsEntity).where(
                AnalyticsEntity.season_id == season.id,
                AnalyticsEntity.key == key,
            )
            result = await s.execute(stmt)
            return result.scalars().first()

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def get_by_season(
        self,
        season: SeasonEntity,
        session: AsyncSession | None = None,
    ) -> list[AnalyticsEntity]:
        """
        Get all analytics entities for a season.

        :param season: Season entity
        :param session: Optional existing session
        :return: List of analytics entities
        """
        async def _do(s: AsyncSession) -> list[AnalyticsEntity]:
            stmt = select(AnalyticsEntity).where(
                AnalyticsEntity.season_id == season.id,
            )
            result = await s.execute(stmt)
            return list(result.scalars().all())

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def upsert(
        self,
        analytics_entity: AnalyticsEntity,
    ) -> AnalyticsEntity:
        """
        Create or update an analytics entity.

        :param analytics_entity: Analytics entity to upsert
        :return: Created or updated entity
        """
        existing = await self.get_by_source(
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
            result = await self.create(analytics_entity)
            return result if result is not None else analytics_entity
