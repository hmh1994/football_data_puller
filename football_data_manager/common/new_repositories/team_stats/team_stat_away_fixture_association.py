from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    TEAM_STATS_TABLE_NAME,
    FIXTURES_TABLE_NAME,
)


class TeamStatAwayFixtureAssociation(Base):
    __tablename__ = "team_stat_away_fixture_association"

    team_stat_id = Column(
        String, ForeignKey(f"{TEAM_STATS_TABLE_NAME}.id"), primary_key=True
    )
    fixture_id = Column(
        String, ForeignKey(f"{FIXTURES_TABLE_NAME}.id"), primary_key=True
    )
    kickoff_time = Column(DateTime, nullable=False)

    team_stat = relationship(
        "TeamStatEntity",
        back_populates="away_fixture_associations",
    )
    fixture = relationship(
        "FixtureEntity",
        back_populates="team_stat_away_fixtures_association",
    )
