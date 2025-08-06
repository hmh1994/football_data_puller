from sqlalchemy import String, Column, ForeignKey, Integer
from sqlalchemy.orm import backref, relationship

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    MATCH_AWAY_TEAM_SUBSTITUTION_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchAwayTeamSubstitutionAssociation(Base):
    """
    Association class for away team substitutions.

    Associates player substitutions (in/out) with the time they occurred for a specific match.

    :ivar match_id: Foreign key to the match entity
    :ivar in_player_id: Foreign key to the player coming in
    :ivar out_player_id: Foreign key to the player going out
    :ivar clock: Time in minutes when the substitution occurred
    """

    __tablename__ = MATCH_AWAY_TEAM_SUBSTITUTION_ASSOCIATION_TABLE_NAME

    SUBSTITUTION_COLLECTION_NAME = "away_team_substitution_associations"

    match_id = Column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    in_player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    out_player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    clock = Column(Integer, nullable=False)

    match = relationship(
        "MatchEntity",
        backref=backref(
            name=SUBSTITUTION_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="MatchAwayTeamSubstitutionAssociation.clock",
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
        Initialize a new away team substitution association.

        :param match: Match entity where the substitution occurred
        :param in_player: Player entity coming into the match
        :param out_player: Player entity being substituted out
        :param clock: Time in minutes when the substitution occurred
        """
        super().__init__()
        self.match_id = match.id
        self.in_player_id = in_player.id
        self.out_player_id = out_player.id
        self.clock = clock

    @property
    def substitution(self):
        """
        Get substitution information as a tuple.

        :returns: Tuple containing ((in_player_id, out_player_id), clock)
        """
        return (self.in_player_id, self.out_player_id), self.clock
