from football_data_manager.repository.entities.news_team_association import (
    NewsTeamAssociation,
)
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.entities.news import NewsEntity
from football_data_manager.repository.repositories.base import AsyncBaseRepository
from football_data_manager.repository.session import SessionFactory


class NewsRepository(AsyncBaseRepository[NewsEntity]):
    """Repository for news entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, NewsEntity)

    async def load_team_associations(self, news: NewsEntity) -> NewsEntity:
        """Load team associations for news."""
        return await self._load_lazy_fields(
            news,
            [NewsTeamAssociation.TEAM_COLLECTION_NAME],
        )

    async def append_teams(self, news: NewsEntity, teams: list[TeamEntity]) -> NewsEntity:
        """Append team associations to news with deduplication."""
        merged = await self.load_team_associations(news)
        existing_team_ids = {assoc.team_id for assoc in merged.team_associations}
        for team in teams:
            if team.id in existing_team_ids:
                continue
            merged.team_associations.append(NewsTeamAssociation(news=merged, team=team))
            existing_team_ids.add(team.id)
        return merged
