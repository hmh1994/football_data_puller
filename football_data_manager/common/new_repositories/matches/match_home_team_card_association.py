from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.enums.CardTypeEnum import CardTypeEnum
from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    MATCH_HOME_TEAM_GOAL_ASSOCIATION_TABLE_NAME,
    MATCHES_TABLE_NAME,
)


class MatchHomeTeamCardAssociation(Base):
    __tablename__ = MATCH_HOME_TEAM_GOAL_ASSOCIATION_TABLE_NAME

    CARD_INFO_COLLECTION_NAME = "home_team_card_associations"
    CARD_INFO_ATTRIBUTE_NAME = "card_info"  # see `card_info` property below

    match_id = Column(String, ForeignKey(f"{MATCHES_TABLE_NAME}.id"), primary_key=True)
    match = relationship(
        argument="MatchEntity",
        backref=backref(
            name=CARD_INFO_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by=f"{__qualname__}.clock",  # see `clock` attribute below
        ),
    )
    card_player_id = Column(
        String, ForeignKey(f"{MATCHES_TABLE_NAME}.id"), primary_key=True
    )
    card_player = relationship(
        argument="PlayerEntity", lazy="noload", foreign_keys=card_player_id
    )
    card_type = Column(Enum(CardTypeEnum), primary_key=True)
    clock = Column(  # see `order_by` in `match` relationship above
        String, nullable=False
    )

    @property
    def card_info(self):  # see `CARD_INFO_ATTRIBUTE_NAME`
        return self.card_player, self.card_type, self.clock
