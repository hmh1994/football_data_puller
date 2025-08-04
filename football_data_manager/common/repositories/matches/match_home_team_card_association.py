from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.repositories.constants import (
    MATCH_HOME_TEAM_CARD_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
    AbstractMatchCardAssociation,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchHomeTeamCardAssociation(AbstractMatchCardAssociation):
    """
    Concrete association class for home team card events.

    Associates cards (yellow/red) issued to home team players during a match.
    Extends AbstractMatchCardAssociation with match-specific relationship.

    :ivar player_id: Foreign key to the player who received the card
    :ivar player: Player entity who received the card
    :ivar card_type: Type of card issued (yellow or red)
    :ivar clock: Time in minutes when the card was issued
    :ivar match_id: Foreign key to the match entity
    :ivar match: Associated match entity with backref to card collection
    """

    __tablename__ = MATCH_HOME_TEAM_CARD_ASSOCIATION_TABLE_NAME

    CARD_INFO_COLLECTION_NAME = "home_team_card_associations"

    match_id = Column(String, ForeignKey(MatchEntity.id), primary_key=True)
    match = relationship(
        MatchEntity,
        backref=backref(
            CARD_INFO_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="MatchHomeTeamCardAssociation.clock",
        ),
    )

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
        super().__init__(player_id=player.id, card_type=card_type, clock=clock)
        self.match_id = match.id
