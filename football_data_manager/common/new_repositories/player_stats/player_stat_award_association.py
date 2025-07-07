from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    PLAYER_STAT_AWARD_ASSOCIATION_TABLE_NAME,
    PLAYER_STATS_TABLE_NAME,
    AWARDS_TABLE_NAME,
)


class PlayerStatAwardAssociation(Base):
    __tablename__ = PLAYER_STAT_AWARD_ASSOCIATION_TABLE_NAME

    AWARD_COLLECTION_NAME = "award_associations"
    PLAYER_STAT_COLLECTION_NAME = "player_stat_awards_associations"

    player_stat_id = Column(
        String, ForeignKey(f"{PLAYER_STATS_TABLE_NAME}.id"), primary_key=True
    )
    award_id = Column(String, ForeignKey(f"{AWARDS_TABLE_NAME}.id"), primary_key=True)
    # TODO: remove primary key constraint and add unique and non-null constraint from the `award_id`
    date = Column(DateTime, nullable=False)

    player_stat = relationship(
        argument="PlayerStatEntity",
        backref=backref(
            name=AWARD_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by=f"{PLAYER_STAT_AWARD_ASSOCIATION_TABLE_NAME}.date",
        ),
    )
    award = relationship(
        argument="AwardEntity",
        backref=backref(name=PLAYER_STAT_COLLECTION_NAME, lazy="noload"),
    )
