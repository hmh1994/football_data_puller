from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    NEWS_TEAM_ASSOCIATION_TABLE_NAME,
    NEWS_TABLE_NAME,
    TEAMS_TABLE_NAME,
)


class NewsTeamAssociation(Base):
    __tablename__ = NEWS_TEAM_ASSOCIATION_TABLE_NAME

    TEAM_COLLECTION_NAME = "team_associations"
    NEWS_COLLECTION_NAME = "news_teams_associations"

    news_id = Column(String, ForeignKey(f"{NEWS_TABLE_NAME}.id"), primary_key=True)
    team_id = Column(String, ForeignKey(f"{TEAMS_TABLE_NAME}.id"), primary_key=True)
    # TODO: remove primary key constraint and add unique and non-null constraint from the `team_id`

    news = relationship(
        argument="NewsEntity",
        backref=backref(
            name=TEAM_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
        ),
    )
    team = relationship(
        argument="TeamEntity",
        backref=backref(name=NEWS_COLLECTION_NAME, lazy="noload"),
    )
