from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.news.news_entity import NewsEntity
from football_data_manager.common.old_repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.db.db_service import DbService


class NewsRepository(BaseRepository[NewsEntity]):
    """
    Player statistics repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, NewsEntity)

    @BaseRepository.with_db_session
    async def load_teams(self, session: AsyncSession, news: NewsEntity) -> NewsEntity:
        """
        Load teams for the given news entity.
        This method uses lazy loading to fetch the teams associated with the news entity.
        :param session: Database session.
        :param news: The news entity to load teams for.
        :return: The news entity with teams loaded.
        """
        return await self._load_lazy_fields(session, news, ["teams"])

    async def append_teams(
        self, news: NewsEntity, teams: list[TeamEntity]
    ) -> NewsEntity:
        """
        Append teams to the news entity.
        This method checks if the teams already exist in the news entity.
        :param news: The news entity to append teams to.
        :param teams: A list of team entities to append.
        :return: The updated news entity with the teams appended if they did not already exist.
        """
        merged_news = await self.load_teams(news)
        team_id_list = [a.id for a in merged_news.teams]
        for team in teams:
            if team.id in team_id_list:
                # If the award already exists, we do not need to update it
                continue
            else:
                # If the award does not exist, we add the award to the player stat with creating a new association
                merged_news.teams.append(team)
        return merged_news
