from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    TEAM_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME,
    TEAMS_TABLE_NAME,
    SEASONS_TABLE_NAME,
)


class TeamChampionshipAssociation(Base):
    __tablename__ = TEAM_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME

    TEAM_COLLECTION_NAME = "team_championships_associations"
    SEASON_COLLECTION_NAME = "season_associations"
    SEASON_ATTRIBUTE_NAME = "season"

    team_id = Column(String, ForeignKey(f"{TEAMS_TABLE_NAME}.id"), primary_key=True)
    season_id = Column(String, ForeignKey(f"{SEASONS_TABLE_NAME}.id"), primary_key=True)
    # TODO: remove primary key constraint and add unique and non-null constraint from the `season_id`
    date_end = Column(DateTime, nullable=False)

    team = relationship(
        argument="TeamEntity",
        backref=backref(
            name=SEASON_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="TeamChampionshipAssociation.date_end",
        ),
    )
    season = relationship(
        "SeasonEntity", backref=backref(name=TEAM_COLLECTION_NAME, lazy="noload")
    )
