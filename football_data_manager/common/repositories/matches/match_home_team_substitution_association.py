from sqlalchemy import String, Column, ForeignKey
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories.constants import (
    MATCH_HOME_TEAM_SUBSTITUTION_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
    AbstractMatchSubstitutionAssociation,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchHomeTeamSubstitutionAssociation(AbstractMatchSubstitutionAssociation):
    """
    Concrete association class for home team substitutions.

    Associates player substitutions (in/out) with the time they occurred.
    Extends AbstractMatchSubstitutionAssociation with match-specific relationship.

    :ivar match_id: Foreign key to the match entity
    :ivar match: Associated match entity with backref to substitution collection
    """

    __tablename__ = MATCH_HOME_TEAM_SUBSTITUTION_ASSOCIATION_TABLE_NAME

    SUBSTITUTION_COLLECTION_NAME = "home_team_substitution_associations"

    match_id = Column(String, ForeignKey(MatchEntity.id), primary_key=True)
    match = relationship(
        MatchEntity,
        backref=backref(
            SUBSTITUTION_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="MatchHomeTeamSubstitutionAssociation.clock",
        ),
    )

    def __init__(
        self,
        match: MatchEntity,
        in_player: PlayerEntity,
        out_player: PlayerEntity,
        clock: int,
    ):
        """
        Initialize a new home team substitution association.

        :param match: Match entity where the substitution occurred
        :param in_player: Player entity coming into the match
        :param out_player: Player entity being substituted out
        :param clock: Time in minutes when the substitution occurred
        """
        super().__init__(
            in_player_id=in_player.id,
            out_player_id=out_player.id,
            clock=clock,
        )
        self.match_id = match.id
