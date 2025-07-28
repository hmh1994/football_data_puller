from sqlalchemy import Column, String, ForeignKey, Enum, Integer
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    MATCH_HOME_TEAM_CARD_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.new_repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.new_repositories.players.player_entity import (
    PlayerEntity,
)


class MatchHomeTeamCardAssociation(Base):
    __tablename__ = MATCH_HOME_TEAM_CARD_ASSOCIATION_TABLE_NAME

    CARD_INFO_COLLECTION_NAME = "home_team_card_associations"

    match_id = Column(String, ForeignKey(MatchEntity.id), primary_key=True)
    match = relationship(
        argument=MatchEntity,
        backref=backref(
            name=CARD_INFO_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by=f"{__qualname__}.clock",  # see `clock` attribute below
        ),
    )
    player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    player = relationship(argument=PlayerEntity, lazy="noload", foreign_keys=player_id)
    card_type = Column(Enum(CardTypeEnum), primary_key=True)
    clock = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )

    @property
    def card_info(self):
        return self.player.id, self.card_type, self.clock
