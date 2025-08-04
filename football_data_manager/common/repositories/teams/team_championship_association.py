from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    TEAM_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME,
    TEAMS_TABLE_NAME,
    SEASONS_TABLE_NAME,
)
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.repositories.teams.team_entity import TeamEntity


class TeamChampionshipAssociation(Base):
    """
    Association class for team championship relationships.
    
    Associates teams with championship seasons they participated in,
    providing a many-to-many relationship between teams and seasons.
    Tracks the end date of each championship for chronological ordering.
    
    :ivar team_id: Foreign key to the team entity
    :ivar season_id: Foreign key to the season entity  
    :ivar date_end: End date of the championship season
    :ivar team: Associated team entity with backref to season collection
    :ivar season: Associated season entity with backref to team collection
    """
    
    __tablename__ = TEAM_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME

    TEAM_COLLECTION_NAME = "team_championships_associations"
    SEASON_COLLECTION_NAME = "season_associations"
    SEASON_ATTRIBUTE_NAME = "season"

    team_id = Column(String, ForeignKey(f"{TEAMS_TABLE_NAME}.id"), primary_key=True)
    season_id = Column(String, ForeignKey(f"{SEASONS_TABLE_NAME}.id"), primary_key=True)
    date_end = Column(DateTime, nullable=False)

    team = relationship(
        "TeamEntity",
        backref=backref(
            SEASON_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="TeamChampionshipAssociation.date_end",
        ),
    )
    season = relationship(
        "SeasonEntity", backref=backref(TEAM_COLLECTION_NAME, lazy="noload")
    )
    
    def __init__(self, team: TeamEntity, season: SeasonEntity, date_end: datetime):
        """
        Initialize a new team championship association.
        
        Creates an association between a team and a championship season,
        accepting entity objects and extracting IDs automatically following
        the entity-based constructor pattern.
        
        :param team: Team entity participating in the championship
        :param season: Season entity for the championship
        :param date_end: End date of the championship season
        """
        self.team_id = team.id
        self.season_id = season.id
        self.date_end = date_end
