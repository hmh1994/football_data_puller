from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import backref, relationship

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    MATCH_HOME_TEAM_SUBSTITUTE_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchHomeTeamSubstituteAssociation(Base):
    """
    Association class for home team substitute players.

    Associates substitute players (bench) with their shirt numbers for a specific match.

    :ivar match_id: Foreign key to the match entity
    :ivar player_id: Foreign key to the substitute player
    :ivar shirt_number: Player's shirt number for the match
    """

    __tablename__ = MATCH_HOME_TEAM_SUBSTITUTE_ASSOCIATION_TABLE_NAME

    PLAYER_INFO_COLLECTION_NAME = "home_team_substitute_associations"

    match_id = Column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    shirt_number = Column(Integer, nullable=False)
    
    match = relationship(
        "MatchEntity",
        backref=backref(
            name=PLAYER_INFO_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="MatchHomeTeamSubstituteAssociation.shirt_number",
        ),
    )

    @property
    def player_info(self):
        """
        Get player information as a tuple.

        :returns: Tuple containing player ID and shirt number
        """
        return self.player_id, self.shirt_number

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        shirt_number: int,
    ):
        """
        Initialize a new home team substitute association.

        :param match: Match entity for the substitute
        :param player: Player entity on the substitute bench
        :param shirt_number: Player's shirt number for the match
        """
        self.match_id = match.id
        self.player_id = player.id
        self.shirt_number = shirt_number
