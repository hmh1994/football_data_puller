from sqlalchemy import Column, String, ForeignKey, Integer, Boolean
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    MATCH_GOAL_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchGoalAssociation(Base):
    """
    Unified association class for match goal events.

    Associates goals scored by players during a match, with a flag
    to distinguish between home and away team goals.

    :ivar match_id: Foreign key to the match entity
    :ivar player_id: Foreign key to the player who scored the goal
    :ivar assist_player_id: Foreign key to the player who provided the assist
    :ivar index: Index of the goal in the match (for ordering)
    :ivar clock: Time in minutes when the goal was scored
    :ivar is_penalty: Whether the goal was scored from a penalty
    :ivar is_own_goal: Whether the goal was an own goal
    :ivar is_home: Flag indicating if the goal was for the home team
    """

    __tablename__ = MATCH_GOAL_ASSOCIATION_TABLE_NAME

    GOAL_INFO_COLLECTION_NAME = "goal_associations"

    match_id = Column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    match = relationship(
        "MatchEntity",
        backref=backref(
            name=GOAL_INFO_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="MatchGoalAssociation.clock",
        ),
    )
    player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    assist_player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    index = Column(Integer, nullable=False, primary_key=True)
    clock = Column(Integer, nullable=False)
    is_penalty = Column(Boolean, nullable=False)
    is_own_goal = Column(Boolean, nullable=False)
    is_home = Column(Boolean, nullable=False, primary_key=True)

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        index: int,
        clock: int,
        is_penalty: bool,
        is_own_goal: bool,
        is_home: bool,
        assist_player: PlayerEntity | None = None,
    ):
        """
        Initialize a new goal association.

        :param match: Match entity where the goal was scored
        :param player: Player entity who scored the goal
        :param index: Index of the goal in the match (for ordering)
        :param clock: Time in minutes when the goal was scored
        :param is_penalty: Whether the goal was scored from a penalty
        :param is_own_goal: Whether the goal was an own goal
        :param is_home: Whether the goal was for the home team
        :param assist_player: Player entity who provided the assist (optional)
        """
        super().__init__()
        self.match_id = match.id
        self.player_id = player.id
        self.assist_player_id = assist_player.id if assist_player else None
        self.index = index
        self.clock = clock
        self.is_penalty = is_penalty
        self.is_own_goal = is_own_goal
        self.is_home = is_home

    @property
    def goal_info(self):
        """
        Get goal information as a tuple.

        :returns: Tuple containing player ID, assist player ID, time, penalty flag, own goal flag, and home flag
        """
        return (
            self.player_id,
            self.assist_player_id,
            self.clock,
            self.is_penalty,
            self.is_own_goal,
            self.is_home,
        )