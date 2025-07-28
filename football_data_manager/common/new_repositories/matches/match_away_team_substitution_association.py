from sqlalchemy import String, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    MATCH_AWAY_TEAM_SUBSTITUTION_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.new_repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.new_repositories.players.player_entity import (
    PlayerEntity,
)


class MatchAwayTeamSubstitutionAssociation(Base):
    __tablename__ = MATCH_AWAY_TEAM_SUBSTITUTION_ASSOCIATION_TABLE_NAME

    SUBSTITUTION_COLLECTION_NAME = "away_team_substitution_associations"

    match_id = Column(String, ForeignKey(MatchEntity.id), primary_key=True)
    match = relationship(
        argument=MatchEntity,
        backref=backref(
            name=SUBSTITUTION_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by=f"{__qualname__}.clock",  # see `clock` attribute below
        ),
    )
    in_player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    in_player = relationship(
        argument=PlayerEntity,
        lazy="noload",
        foreign_keys=in_player_id,
    )
    out_player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    out_player = relationship(
        argument=PlayerEntity,
        lazy="noload",
        foreign_keys=out_player_id,
    )
    clock = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )

    @property
    def substitution(self):
        return (self.in_player.id, self.out_player.id), self.clock
