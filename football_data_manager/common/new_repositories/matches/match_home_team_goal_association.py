from sqlalchemy import Column, String, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.new_repositories import Base
from football_data_manager.common.new_repositories.constants import (
    MATCH_HOME_TEAM_GOAL_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.new_repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.new_repositories.players.player_entity import (
    PlayerEntity,
)


class MatchHomeTeamGoalAssociation(Base):
    __tablename__ = MATCH_HOME_TEAM_GOAL_ASSOCIATION_TABLE_NAME

    GOAL_INFO_COLLECTION_NAME = "home_team_goal_associations"

    match_id = Column(String, ForeignKey(MatchEntity.id), primary_key=True)
    match = relationship(
        argument=MatchEntity,
        backref=backref(
            name=GOAL_INFO_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by=f"{__qualname__}.clock",  # see `clock` attribute below
        ),
    )
    player_id = Column(String, ForeignKey(PlayerEntity.id), primary_key=True)
    player = relationship(
        argument="PlayerEntity", lazy="noload", foreign_keys=player_id
    )
    assist_player_id = Column(String, ForeignKey(PlayerEntity.id), nullable=True)
    assist_player = relationship(
        argument="PlayerEntity",
        lazy="noload",
        foreign_keys=assist_player_id,
    )
    clock = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )
    is_penalty = Column(Boolean, nullable=False)
    is_own_goal = Column(Boolean, nullable=False)

    @property
    def goal_info(self):
        return (
            self.player.id,
            self.assist_player.id,
            self.clock,
            self.is_penalty,
            self.is_own_goal,
        )
