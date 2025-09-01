from sqlalchemy import Column, String, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    MATCH_LINEUP_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchLineupAssociation(Base):
    """
    Unified association class for match lineup positions.

    Associates starting lineup players with their formation positions and shirt numbers,
    with a flag to distinguish between home and away team players.

    :ivar match_id: Foreign key to the match entity
    :ivar player_id: Foreign key to the player in the lineup
    :ivar position: Player's position in the formation
    :ivar shirt_number: Player's shirt number for the match
    :ivar row: Formation row position (1-based)
    :ivar column: Formation column position (1-based)
    :ivar is_home: Flag indicating if the player is in the home team lineup
    """

    __tablename__ = MATCH_LINEUP_ASSOCIATION_TABLE_NAME

    POSITION_COLLECTION_NAME = "lineup_associations"

    match_id = Column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    match = relationship(
        "MatchEntity",
        backref=backref(
            name=POSITION_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="MatchLineupAssociation.shirt_number",
        ),
    )
    player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    position = Column(Enum(PositionEnum), nullable=False)
    shirt_number = Column(Integer, nullable=False)
    row = Column(Integer, nullable=False)
    column = Column(Integer, nullable=False)
    is_home = Column(Boolean, nullable=False, primary_key=True)

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        position: PositionEnum,
        shirt_number: int,
        row: int,
        column: int,
        is_home: bool,
    ):
        """
        Initialize a new lineup association.

        :param match: Match entity for the lineup
        :param player: Player entity in the starting lineup
        :param position: Player's position in the formation
        :param shirt_number: Player's shirt number for the match
        :param row: Formation row position (1-based)
        :param column: Formation column position (1-based)
        :param is_home: Whether the player is in the home team lineup
        """
        super().__init__()
        self.match_id = match.id
        self.player_id = player.id
        self.position = position
        self.shirt_number = shirt_number
        self.row = row
        self.column = column
        self.is_home = is_home

    @property
    def player_info(self):
        """
        Get player lineup information as a tuple.

        :returns: Tuple containing player ID, shirt number, position coordinates, and home flag
        """
        return self.player_id, self.shirt_number, (self.row, self.column), self.is_home