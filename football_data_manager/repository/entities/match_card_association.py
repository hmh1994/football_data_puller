from sqlalchemy import String, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.players import PlayerEntity

MATCH_CARD_ASSOCIATION_TABLE_NAME = "match_card_association"


class MatchCardAssociation(Base):
    """
    Association class for match card events.

    :ivar match_id: Foreign key to the match entity
    :ivar player_id: Foreign key to the player who received the card
    :ivar index: Index of the card in the match
    :ivar card_type: Type of card issued
    :ivar clock: Time in minutes when the card was issued
    :ivar is_home: Flag indicating if the card was for a home team player
    """

    __tablename__ = MATCH_CARD_ASSOCIATION_TABLE_NAME

    CARD_INFO_COLLECTION_NAME = "card_associations"

    match_id: Mapped[str] = mapped_column(
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
    player_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    index: Mapped[int] = mapped_column(Integer, nullable=False, primary_key=True)
    card_type: Mapped[CardTypeEnum] = mapped_column(
        Enum(CardTypeEnum), primary_key=True
    )
    clock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_home: Mapped[bool] = mapped_column(Boolean, nullable=False, primary_key=True)

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
        :param index: Index of the card in the match
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
