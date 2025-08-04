from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories.constants import (
    MATCH_HOME_TEAM_GOAL_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
    AbstractMatchGoalAssociation,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchHomeTeamGoalAssociation(AbstractMatchGoalAssociation):
    """
    Concrete association class for home team goal events.

    Associates goals scored by home team players during a match.
    Extends AbstractMatchGoalAssociation with match-specific relationship.

    :ivar player_id: Foreign key to the player who scored the goal
    :ivar player: Player entity who scored the goal
    :ivar assist_player_id: Foreign key to the player who provided the assist
    :ivar assist_player: Player entity who provided the assist
    :ivar clock: Time in minutes when the goal was scored
    :ivar is_penalty: Whether the goal was scored from a penalty
    :ivar is_own_goal: Whether the goal was an own goal
    :ivar match_id: Foreign key to the match entity
    :ivar match: Associated match entity with backref to goal collection
    """

    __tablename__ = MATCH_HOME_TEAM_GOAL_ASSOCIATION_TABLE_NAME

    GOAL_INFO_COLLECTION_NAME = "home_team_goal_associations"

    match_id = Column(String, ForeignKey(MatchEntity.id), primary_key=True)
    match = relationship(
        MatchEntity,
        backref=backref(
            GOAL_INFO_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="MatchHomeTeamGoalAssociation.clock",
        ),
    )

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        clock: int,
        is_penalty: bool,
        is_own_goal: bool,
        assist_player: PlayerEntity | None = None,
    ):
        """
        Initialize a new home team goal association.

        :param match: Match entity where the goal was scored
        :param player: Player entity who scored the goal
        :param clock: Time in minutes when the goal was scored
        :param is_penalty: Whether the goal was scored from a penalty
        :param is_own_goal: Whether the goal was an own goal
        :param assist_player: Player entity who provided the assist (optional)
        """
        super().__init__(
            player_id=player.id,
            assist_player_id=assist_player.id if assist_player else None,
            clock=clock,
            is_penalty=is_penalty,
            is_own_goal=is_own_goal,
        )
        self.match_id = match.id
