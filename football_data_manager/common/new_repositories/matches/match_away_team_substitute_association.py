from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    MATCH_AWAY_TEAM_SUBSTITUTE_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.new_repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.new_repositories.players.player_entity import (
    PlayerEntity,
)


class MatchAwayTeamSubstituteAssociation(Base):
    __tablename__ = MATCH_AWAY_TEAM_SUBSTITUTE_ASSOCIATION_TABLE_NAME

    PLAYER_INFO_COLLECTION_NAME = "away_team_substitute_associations"

    match_id = Column(String, ForeignKey(MatchEntity.id), primary_key=True)
    match = relationship(
        argument=MatchEntity,
        backref=backref(
            name=PLAYER_INFO_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by=f"{__qualname__}.shirt_number",  # see `shirt_number` attribute below
        ),
    )
    player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    player = relationship(argument=PlayerEntity, lazy="noload", foreign_keys=player_id)
    shirt_number = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )

    @property
    def player_info(self):
        return self.player.id, self.shirt_number
