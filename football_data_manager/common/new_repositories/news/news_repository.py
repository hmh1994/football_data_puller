from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.news.news_entity import NewsEntity
from football_data_manager.common.services.db.db_service import DbService


class NewsRepository(BaseRepository[NewsEntity]):
    """
    Player statistics repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, NewsEntity)

    @BaseRepository.with_db_session
    async def load_lazy_fields(
        self, session: AsyncSession, news: NewsEntity
    ) -> NewsEntity:
        """
        Load lazy fields for the news entity.
        Fields for lazy loading include `teams`.
        :param session: The database session.
        :param news: The news entity to load lazy fields for.
        :return: The news entity with lazy fields loaded.
        """
        merged_entity = await session.merge(news)
        await session.refresh(merged_entity, attribute_names=["teams"])
        return merged_entity
