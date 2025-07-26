from sqlalchemy import Column, String, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.new_repositories.constants import (
    MATCH_AWAY_TEAM_GOAL_ASSOCIATION_TABLE_NAME,
    MATCHES_TABLE_NAME,
    PLAYERS_TABLE_NAME,
)


class MatchAwayTeamGoalAssociation:
    __tablename__ = MATCH_AWAY_TEAM_GOAL_ASSOCIATION_TABLE_NAME

    GOAL_INFO_COLLECTION_NAME = "away_team_goal_associations"
    GOAL_INFO_ATTRIBUTE_NAME = "goal_info"  # see `goal_info` property below

    match_id = Column(String, ForeignKey(f"{MATCHES_TABLE_NAME}.id"), primary_key=True)
    match = relationship(
        argument="MatchEntity",
        backref=backref(
            name=GOAL_INFO_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by=f"{__qualname__}.clock",  # see `clock` attribute below
        ),
    )
    goal_player_id = Column(
        String, ForeignKey(f"{PLAYERS_TABLE_NAME}.id"), primary_key=True
    )
    goal_player = relationship(
        argument="PlayerEntity", lazy="noload", foreign_keys=goal_player_id
    )
    assist_player_id = Column(
        String, ForeignKey(f"{PLAYERS_TABLE_NAME}.id"), nullable=True
    )
    assist_player = relationship(
        argument="PlayerEntity",
        lazy="noload",
        foreign_keys=assist_player_id,
        nullable=True,
    )
    clock = Column(  # see `order_by` in `match` relationship above
        Integer, nullable=False
    )
    is_penalty = Column(Boolean, nullable=False)
    is_own_goal = Column(Boolean, nullable=False)

    @property
    def goal_info(self):  # see `GOAL_INFO_ATTRIBUTE_NAME`
        return (
            self.goal_player,
            self.assist_player,
            self.clock,
            self.is_penalty,
            self.is_own_goal,
        )
