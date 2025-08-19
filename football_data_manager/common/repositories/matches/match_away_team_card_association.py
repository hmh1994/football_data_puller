from sqlalchemy import Column, String, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    MATCH_AWAY_TEAM_CARD_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchAwayTeamCardAssociation(Base):
    """
    Concrete association class for away team card events.

    Associates cards (yellow/red) issued to away team players during a match.

    :ivar match_id: Foreign key to the match entity
    :ivar player_id: Foreign key to the player who received the card
    :ivar index: Index of the card in the match (for ordering)
    :ivar card_type: Type of card issued (yellow or red)
    :ivar clock: Time in minutes when the card was issued
    """

    __tablename__ = MATCH_AWAY_TEAM_CARD_ASSOCIATION_TABLE_NAME

    CARD_INFO_COLLECTION_NAME = "away_team_card_associations"

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
            order_by="MatchAwayTeamCardAssociation.clock",
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

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        index: int,
        card_type: CardTypeEnum,
        clock: int,
    ):
        """
        Initialize a new away team card association.

        :param match: Match entity where the card was issued
        :param player: Player entity who received the card
        :param index: Index of the card in the match (for ordering)
        :param card_type: Type of card (yellow or red)
        :param clock: Time in minutes when the card was issued
        """
        super().__init__()
        self.match_id = match.id
        self.player_id = player.id
        self.index = index
        self.card_type = card_type
        self.clock = clock

    @property
    def card_info(self):
        """
        Get card information as a tuple.

        :returns: Tuple containing player ID, card type, and time
        """
        return self.player_id, self.card_type, self.clock
