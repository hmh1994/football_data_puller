from sqlalchemy import Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    MATCH_HOME_TEAM_LINEUP_ASSOCIATION_TABLE_NAME,
    MATCHES_TABLE_NAME,
    PLAYERS_TABLE_NAME,
)


class MatchHomeTeamLineupAssociation(Base):
    __tablename__ = MATCH_HOME_TEAM_LINEUP_ASSOCIATION_TABLE_NAME

    POSITION_COLLECTION_NAME = "home_team_lineup_associations"
    POSITION_ATTRIBUTE_NAME = "player_info"  # see `player_info` property below

    match_id = Column(String, ForeignKey(f"{MATCHES_TABLE_NAME}.id"), primary_key=True)
    match = relationship(
        argument="MatchEntity",
        backref=backref(
            name=POSITION_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by=f"{__qualname__}.shirt_number",  # see `shirt_number` attribute below
        ),
    )
    player_id = Column(String, ForeignKey(f"{PLAYERS_TABLE_NAME}.id"), primary_key=True)
    player = relationship(
        argument="PlayerEntity", lazy="noload", foreign_keys=player_id
    )
    shirt_number = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )
    row = Column(Integer, nullable=False)
    column = Column(Integer, nullable=False)

    @property
    def player_info(self):  # see `POSITION_ATTRIBUTE_NAME`
        return self.player, self.shirt_number, (self.row, self.column)
