from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    TEAM_STAT_MATCH_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import MatchEntity
from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)


class TeamStatMatchAssociation(Base):
    """
    Association class for team stat match relationships.

    Associates team statistics with matches (both home and away),
    tracking kickoff times for proper ordering and game scheduling.

    :ivar team_stat_id: Foreign key to the team stat entity
    :ivar match_id: Foreign key to the match entity
    :ivar kickoff_time: Scheduled kickoff time for the match
    """

    __tablename__ = TEAM_STAT_MATCH_ASSOCIATION_TABLE_NAME

    MATCH_COLLECTION_NAME = "match_associations"

    match_id = Column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
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
            name=MATCH_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="TeamStatMatchAssociation.kickoff_time",
        ),
    )
    kickoff_time = Column(DateTime, nullable=False)
    is_home = Column(Boolean, nullable=False)

    def __init__(
        self,
        team_stat: TeamStatEntity,
        match: MatchEntity,
        kickoff_time: datetime,
        is_home: bool,
    ):
        """
        Initialize a new team stat match association.

        :param team_stat: Team stat entity for match
        :param match: Match entity for the match
        :param kickoff_time: Scheduled kickoff time for the match
        """
        super().__init__()
        self.match_id = match.id
        self.kickoff_time = kickoff_time
        self.team_stat_id = team_stat.id
        self.is_home = is_home
