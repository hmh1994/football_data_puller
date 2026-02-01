from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.teams import TeamEntity

TEAM_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME = "team_championship_association"


class TeamChampionshipAssociation(Base):
    """
    Association class for team championship relationships.

    :ivar team_id: Foreign key to the team entity
    :ivar season_id: Foreign key to the season entity
    :ivar date_end: End date of the championship season
    """

    __tablename__ = TEAM_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME

    SEASON_COLLECTION_NAME = "championship_season_associations"

    season_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("seasons.id", ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    team_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    team = relationship(
        TeamEntity,
        backref=backref(
            name=SEASON_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="TeamChampionshipAssociation.date_end",
        ),
    )
    date_end: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    def __init__(self, team, season, date_end: datetime):
        """
        Initialize a new team championship association.

        :param team: Team entity participating in the championship
        :param season: Season entity for the championship
        :param date_end: End date of the championship season
        """
        super().__init__()
        self.season_id = season.id
        self.date_end = date_end
        self.team_id = team.id
