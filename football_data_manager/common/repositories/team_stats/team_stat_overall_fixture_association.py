from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    TEAM_STAT_OVERALL_FIXTURE_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)


class TeamStatOverallFixtureAssociation(Base):
    """
    Association class for team stat overall fixture relationships.

    Associates team statistics with overall fixtures (both home and away),
    tracking kickoff times for proper ordering and game scheduling.

    :ivar team_stat_id: Foreign key to the team stat entity
    :ivar fixture_id: Foreign key to the fixture entity
    :ivar kickoff_time: Scheduled kickoff time for the fixture
    """

    __tablename__ = TEAM_STAT_OVERALL_FIXTURE_ASSOCIATION_TABLE_NAME

    FIXTURE_COLLECTION_NAME = "overall_fixture_associations"

    fixture_id = Column(
        String,
        ForeignKey(FixtureEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    team_stat_id = Column(
        String,
        ForeignKey(TeamStatEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    team_stat = relationship(
        "TeamStatEntity",
        backref=backref(
            name=FIXTURE_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="TeamStatOverallFixtureAssociation.kickoff_time",
        ),
    )
    kickoff_time = Column(DateTime, nullable=False)
    is_home = Column(Boolean, nullable=False)

    def __init__(
        self,
        team_stat: TeamStatEntity,
        fixture: FixtureEntity,
        kickoff_time: datetime,
        is_home: bool,
    ):
        """
        Initialize a new team stat overall fixture association.

        :param team_stat: Team stat entity for overall fixture
        :param fixture: Fixture entity for the match
        :param kickoff_time: Scheduled kickoff time for the fixture
        """
        super().__init__()
        self.fixture_id = fixture.id
        self.kickoff_time = kickoff_time
        self.team_stat_id = team_stat.id
        self.is_home = is_home
