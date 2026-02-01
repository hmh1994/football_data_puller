from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.news.news_entity import NewsEntity
from football_data_manager.common.repositories.news.news_team_association import (
    NewsTeamAssociation,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.db.db_service import DbService


class NewsRepository(BaseRepository[NewsEntity]):
    """
    Repository for managing news entities.

    Provides specialized functionality for handling news articles with multilingual content
    and team associations. Supports team loading and association management operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the news repository.

        :param db_service: Database service for database operations
        """
        super().__init__(db_service, NewsEntity)

    async def load_teams(self, news: NewsEntity) -> NewsEntity:
        """
        Load teams for the given news entity.

        Uses lazy loading to fetch the teams associated with the news entity
        through the team_associations relationship.

        :param news: The news entity to load teams for
        :returns: The news entity with teams loaded
        """
        return await self._load_lazy_fields(
            news, [NewsTeamAssociation.TEAM_COLLECTION_NAME]
        )

    async def append_teams(
        self, news: NewsEntity, teams: list[TeamEntity]
    ) -> NewsEntity:
        """
        Append teams to the news entity.

        Checks if the teams already exist in the news entity and only adds new associations.
        Uses efficient ID-based checking to prevent duplicate team associations.

        :param news: The news entity to append teams to
        :param teams: A list of team entities to append
        :returns: The updated news entity with the teams appended if they did not already exist
        """
        merged_news = await self.load_teams(news)
        existing_team_ids = [
            association.team_id for association in merged_news.team_associations
        ]
        for team in teams:
            if team.id not in existing_team_ids:
                association = NewsTeamAssociation(news=merged_news, team=team)
                merged_news.team_associations.append(association)
        return merged_news
