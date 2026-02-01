from sqlalchemy import Column, String, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    MATCH_SUBSTITUTE_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchSubstituteAssociation(Base):
    """
    Unified association class for match substitute players.

    Associates substitute players (bench) with their shirt numbers and positions,
    with a flag to distinguish between home and away team substitutes.

    :ivar match_id: Foreign key to the match entity
    :ivar player_id: Foreign key to the substitute player
    :ivar position: Player's position
    :ivar shirt_number: Player's shirt number for the match
    :ivar is_home: Flag indicating if the substitute is for the home team
    """

    __tablename__ = MATCH_SUBSTITUTE_ASSOCIATION_TABLE_NAME

    PLAYER_INFO_COLLECTION_NAME = "substitute_associations"

    match_id = Column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    match = relationship(
        "MatchEntity",
        backref=backref(
            name=PLAYER_INFO_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="MatchSubstituteAssociation.shirt_number",
        ),
    )
    player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    position = Column(Enum(PositionEnum), nullable=False)
    shirt_number = Column(Integer, nullable=False)
    is_home = Column(Boolean, nullable=False, primary_key=True)

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        position: PositionEnum,
        shirt_number: int,
        is_home: bool,
    ):
        """
        Initialize a new substitute association.

        :param match: Match entity for the substitute
        :param player: Player entity on the substitute bench
        :param position: Player's position
        :param shirt_number: Player's shirt number for the match
        :param is_home: Whether the substitute is for the home team
        """
        super().__init__()
        self.match_id = match.id
        self.player_id = player.id
        self.position = position
        self.shirt_number = shirt_number
        self.is_home = is_home

