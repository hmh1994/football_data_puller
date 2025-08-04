from datetime import datetime

from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories.constants import (
    TEAM_STATS_TABLE_NAME,
    TEAM_STAT_OVERALL_FIXTURE_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.fixtures.fixture_entity import FixtureEntity
from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    AbstractTeamStatFixtureAssociation,
    TeamStatEntity,
)


class TeamStatOverallFixtureAssociation(AbstractTeamStatFixtureAssociation):
    """
    Association class for team stat overall fixture relationships.
    
    Associates team statistics with overall fixtures (both home and away),
    tracking kickoff times for proper ordering and game scheduling.
    
    :ivar team_stat_id: Foreign key to the team stat entity
    :ivar fixture_id: Foreign key to the fixture entity
    :ivar kickoff_time: Scheduled kickoff time for the fixture
    :ivar team_stat: Associated team stat entity with backref to fixture collection
    :ivar fixture: Associated fixture entity with backref to team stat collection
    """
    
    __tablename__ = TEAM_STAT_OVERALL_FIXTURE_ASSOCIATION_TABLE_NAME

    FIXTURE_COLLECTION_NAME = "overall_fixture_associations"

    team_stat_id = Column(
        String, ForeignKey(f"{TEAM_STATS_TABLE_NAME}.id"), primary_key=True
    )
    team_stat = relationship(
        "TeamStatEntity",
        backref=backref(
            FIXTURE_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="TeamStatOverallFixtureAssociation.kickoff_time",
        ),
    )
    
    def __init__(self, team_stat: TeamStatEntity, fixture: FixtureEntity, kickoff_time: datetime):
        """
        Initialize a new team stat overall fixture association.
        
        :param team_stat: Team stat entity for overall fixture
        :param fixture: Fixture entity for the match
        :param kickoff_time: Scheduled kickoff time for the fixture
        """
        self.team_stat_id = team_stat.id
        self.fixture_id = fixture.id
        self.kickoff_time = kickoff_time
