from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.team_stats import TeamStatEntity

TEAM_STAT_MATCH_ASSOCIATION_TABLE_NAME = "team_stat_match_association"


class TeamStatMatchAssociation(Base):
    """
    Association class for team stat match relationships.

    :ivar match_id: Foreign key to the match entity
    :ivar team_stat_id: Foreign key to the team stat entity
    :ivar kickoff_time: Scheduled kickoff time
    :ivar is_home: Whether this is a home match
    """

    __tablename__ = TEAM_STAT_MATCH_ASSOCIATION_TABLE_NAME

    MATCH_COLLECTION_NAME = "match_associations"

    match_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    team_stat_id: Mapped[str] = mapped_column(
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
    kickoff_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    is_home: Mapped[bool] = mapped_column(Boolean, nullable=False)

    def __init__(
        self,
        team_stat: TeamStatEntity,
        match: MatchEntity,
        kickoff_time: datetime,
        is_home: bool,
    ):
        """
        Initialize a new team stat match association.

        :param team_stat: Team stat entity
        :param match: Match entity
        :param kickoff_time: Scheduled kickoff time
        :param is_home: Whether this is a home match
        """
        super().__init__()
        self.match_id = match.id
        self.kickoff_time = kickoff_time
        self.team_stat_id = team_stat.id
        self.is_home = is_home
