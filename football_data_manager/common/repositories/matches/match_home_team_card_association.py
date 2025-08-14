from sqlalchemy import Column, String, ForeignKey, Enum, Integer
from sqlalchemy.orm import backref, relationship

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    MATCH_HOME_TEAM_CARD_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchHomeTeamCardAssociation(Base):
    """
    Concrete association class for home team card events.

    Associates cards (yellow/red) issued to home team players during a match.
    Extends AbstractMatchCardAssociation with match-specific relationship.

    :ivar player_id: Foreign key to the player who received the card
    :ivar card_type: Type of card issued (yellow or red)
    :ivar clock: Time in minutes when the card was issued
    :ivar match_id: Foreign key to the match entity
    """

    __tablename__ = MATCH_HOME_TEAM_CARD_ASSOCIATION_TABLE_NAME

    CARD_INFO_COLLECTION_NAME = "home_team_card_associations"

    player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    card_type = Column(Enum(CardTypeEnum), primary_key=True)
    clock = Column(Integer, nullable=False)
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
            order_by="MatchHomeTeamCardAssociation.clock",
        ),
    )

    @property
    def card_info(self):
        """
        Get card information as a tuple.

        :returns: Tuple containing player ID, card type, and time
        """
        return self.player_id, self.card_type, self.clock

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        card_type: CardTypeEnum,
        clock: int,
    ):
        """
        Initialize a new home team card association.

        :param match: Match entity where the card was issued
        :param player: Player entity who received the card
        :param card_type: Type of card (yellow or red)
        :param clock: Time in minutes when the card was issued
        """
        super().__init__()
        self.player_id = player.id
        self.card_type = card_type
        self.clock = clock
        self.match_id = match.id
