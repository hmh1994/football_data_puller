from sqlalchemy import Column, String, ForeignKey, Enum, Integer, Boolean
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    MATCH_CARD_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchCardAssociation(Base):
    """
    Unified association class for match card events.

    Associates cards (yellow/red) issued to players during a match, with a flag
    to distinguish between home and away team players.

    :ivar match_id: Foreign key to the match entity
    :ivar player_id: Foreign key to the player who received the card
    :ivar index: Index of the card in the match (for ordering)
    :ivar card_type: Type of card issued (yellow or red)
    :ivar clock: Time in minutes when the card was issued
    :ivar is_home: Flag indicating if the card was for a home team player
    """

    __tablename__ = MATCH_CARD_ASSOCIATION_TABLE_NAME

    CARD_INFO_COLLECTION_NAME = "card_associations"

    match_id = Column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    match = relationship(
        "MatchEntity",
        backref=backref(
            name=CARD_INFO_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="MatchCardAssociation.clock",
        ),
    )
    player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    index = Column(Integer, nullable=False, primary_key=True)
    card_type = Column(Enum(CardTypeEnum), primary_key=True)
    clock = Column(Integer, nullable=False)
    is_home = Column(Boolean, nullable=False, primary_key=True)

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        index: int,
        card_type: CardTypeEnum,
        clock: int,
        is_home: bool,
    ):
        """
        Initialize a new card association.

        :param match: Match entity where the card was issued
        :param player: Player entity who received the card
        :param index: Index of the card in the match (for ordering)
        :param card_type: Type of card (yellow or red)
        :param clock: Time in minutes when the card was issued
        :param is_home: Whether the card was for a home team player
        """
        super().__init__()
        self.match_id = match.id
        self.player_id = player.id
        self.index = index
        self.card_type = card_type
        self.clock = clock
        self.is_home = is_home

