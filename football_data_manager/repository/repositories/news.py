from football_data_manager.repository.entities.news import NewsEntity
from football_data_manager.repository.repositories.base import AsyncBaseRepository
from football_data_manager.repository.session import SessionFactory


class NewsRepository(AsyncBaseRepository[NewsEntity]):
    """Repository for news entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, NewsEntity)
