from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.news import NewsEntity
from football_data_manager.repository.entities.teams import TeamEntity

NEWS_TEAM_ASSOCIATION_TABLE_NAME = "news_team_association"


class NewsTeamAssociation(Base):
    """
    Association class for news-team relationships.

    :ivar news_id: Foreign key to the news entity
    :ivar team_id: Foreign key to the team mentioned in the news
    """

    __tablename__ = NEWS_TEAM_ASSOCIATION_TABLE_NAME

    TEAM_COLLECTION_NAME = "team_associations"

    news_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(NewsEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    news = relationship(
        "NewsEntity",
        backref=backref(
            name=TEAM_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
        ),
    )
    team_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )

    def __init__(self, news: NewsEntity, team: TeamEntity):
        """
        Initialize a new news-team association.

        :param news: News entity that mentions the team
        :param team: Team entity mentioned in the news
        """
        super().__init__()
        self.team_id = team.id
        self.news_id = news.id
