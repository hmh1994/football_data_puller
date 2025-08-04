from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories.constants import (
    NEWS_TEAM_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.news.news_entity import (
    NewsEntity,
    AbstractNewsTeamAssociation,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity


class NewsTeamAssociation(AbstractNewsTeamAssociation):
    """
    Concrete association class for news-team relationships.

    Associates news articles with teams mentioned in the content.
    Extends AbstractNewsTeamAssociation with news-specific relationship.

    :ivar team_id: Foreign key to the team mentioned in the news
    :ivar team: Team entity mentioned in the news
    :ivar news_id: Foreign key to the news entity
    :ivar news: Associated news entity with backref to team collection
    """

    __tablename__ = NEWS_TEAM_ASSOCIATION_TABLE_NAME

    TEAM_COLLECTION_NAME = "news_teams_associations"

    news_id = Column(String, ForeignKey(NewsEntity.id), primary_key=True)
    news = relationship(
        NewsEntity,
        backref=backref(
            TEAM_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
        ),
    )

    def __init__(self, news: NewsEntity, team: TeamEntity):
        """
        Initialize a new news-team association.

        :param news: News entity that mentions the team
        :param team: Team entity mentioned in the news
        """
        super().__init__(team_id=team.id)
        self.news_id = news.id
