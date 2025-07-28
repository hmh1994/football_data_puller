from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    MATCH_HOME_TEAM_LINEUP_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.new_repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.new_repositories.players.player_entity import (
    PlayerEntity,
)


class MatchHomeTeamLineupAssociation(Base):
    __tablename__ = MATCH_HOME_TEAM_LINEUP_ASSOCIATION_TABLE_NAME

    POSITION_COLLECTION_NAME = "home_team_lineup_associations"

    match_id = Column(String, ForeignKey(MatchEntity.id), primary_key=True)
    match = relationship(
        argument="MatchEntity",
        backref=backref(
            name=POSITION_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by=f"{__qualname__}.shirt_number",  # see `shirt_number` attribute below
        ),
    )
    player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    player = relationship(
        argument="PlayerEntity", lazy="noload", foreign_keys=player_id
    )
    shirt_number = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )
    row = Column(Integer, nullable=False)
    column = Column(Integer, nullable=False)

    @property
    def player_info(self):
        return self.player.id, self.shirt_number, (self.row, self.column)
