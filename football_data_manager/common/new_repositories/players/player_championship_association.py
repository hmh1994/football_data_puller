from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    PLAYER_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME,
    SEASONS_TABLE_NAME,
    PLAYERS_TABLE_NAME,
)


class PlayerChampionshipAssociation(Base):
    __tablename__ = PLAYER_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME

    PLAYER_COLLECTION_NAME = "player_championships_associations"
    SEASON_COLLECTION_NAME = "season_associations"
    SEASON_ATTRIBUTE_NAME = "season"

    player_id = Column(String, ForeignKey(f"{PLAYERS_TABLE_NAME}.id"), primary_key=True)
    season_id = Column(String, ForeignKey(f"{SEASONS_TABLE_NAME}.id"), primary_key=True)
    # TODO: remove primary key constraint and add unique and non-null constraint from the `season_id`
    date_end = Column(DateTime, nullable=False)

    player = relationship(
        argument="PlayerEntity",
        backref=backref(
            name=SEASON_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="PlayerChampionshipAssociation.date_end",
        ),
    )
    season = relationship(
        "SeasonEntity", backref=backref(name=PLAYER_COLLECTION_NAME, lazy="noload")
    )
