from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    PLAYER_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME,
    SEASONS_TABLE_NAME,
    PLAYERS_TABLE_NAME,
)


class PlayerChampionshipAssociation(Base):
    __tablename__ = PLAYER_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME

    player_id = Column(String, ForeignKey(f"{PLAYERS_TABLE_NAME}.id"), primary_key=True)
    season_id = Column(String, ForeignKey(f"{SEASONS_TABLE_NAME}.id"), primary_key=True)
    date_end = Column(DateTime, nullable=False)

    season = relationship(
        "SeasonEntity",
        lazy="subquery",
        back_populates="player_championships_associations",
    )
