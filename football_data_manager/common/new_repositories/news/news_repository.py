from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.news.news_entity import NewsEntity
from football_data_manager.common.services.db.db_service import DbService


class NewsRepository(BaseRepository[NewsEntity]):
    """
    Player statistics repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, NewsEntity)
