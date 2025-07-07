from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    TEAM_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME,
    TEAMS_TABLE_NAME,
    SEASONS_TABLE_NAME,
)


class TeamChampionshipAssociation(Base):
    __tablename__ = TEAM_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME

    team_id = Column(String, ForeignKey(f"{TEAMS_TABLE_NAME}.id"), primary_key=True)
    season_id = Column(String, ForeignKey(f"{SEASONS_TABLE_NAME}.id"), primary_key=True)
    date_end = Column(DateTime, nullable=False)

    team = relationship(
        "TeamEntity",
        back_populates="championship_season_associations",
    )
