from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    MATCH_HOME_TEAM_LINEUP_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchHomeTeamLineupAssociation(Base):
    """
    Concrete association class for home team lineup positions.

    Associates starting lineup players with their formation positions and shirt numbers.
    Extends AbstractMatchLineupAssociation with match-specific relationship.

    :ivar match_id: Foreign key to the match entity
    :ivar player_id: Foreign key to the player in the lineup
    :ivar shirt_number: Player's shirt number for the match
    :ivar row: Formation row position (1-based)
    :ivar column: Formation column position (1-based)
    """

    __tablename__ = MATCH_HOME_TEAM_LINEUP_ASSOCIATION_TABLE_NAME

    POSITION_COLLECTION_NAME = "home_team_lineup_associations"

    player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    match_id = Column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    shirt_number = Column(Integer, nullable=False)
    row = Column(Integer, nullable=False)
    column = Column(Integer, nullable=False)
    match = relationship(
        "MatchEntity",
        backref=backref(
            name=POSITION_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="MatchHomeTeamLineupAssociation.shirt_number",
        ),
    )

    @property
    def player_info(self):
        """
        Get player lineup information as a tuple.

        :returns: Tuple containing player ID, shirt number, and position coordinates
        """
        return self.player_id, self.shirt_number, (self.row, self.column)

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        shirt_number: int,
        row: int,
        column: int,
    ):
        """
        Initialize a new home team lineup association.

        :param match: Match entity for the lineup
        :param player: Player entity in the starting lineup
        :param shirt_number: Player's shirt number for the match
        :param row: Formation row position (1-based)
        :param column: Formation column position (1-based)
        """
        self.player_id = player.id
        self.shirt_number = shirt_number
        self.row = row
        self.column = column
        self.match_id = match.id
