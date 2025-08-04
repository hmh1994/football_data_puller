from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories.constants import (
    MATCH_AWAY_TEAM_LINEUP_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
    AbstractMatchLineupAssociation,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchAwayTeamLineupAssociation(AbstractMatchLineupAssociation):
    """
    Concrete association class for away team lineup positions.

    Associates starting lineup players with their formation positions and shirt numbers.
    Extends AbstractMatchLineupAssociation with match-specific relationship.

    :ivar match_id: Foreign key to the match entity
    :ivar match: Associated match entity with backref to lineup collection
    """

    __tablename__ = MATCH_AWAY_TEAM_LINEUP_ASSOCIATION_TABLE_NAME

    POSITION_COLLECTION_NAME = "away_team_lineup_associations"

    match_id = Column(String, ForeignKey(MatchEntity.id), primary_key=True)
    match = relationship(
        MatchEntity,
        backref=backref(
            POSITION_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="MatchAwayTeamLineupAssociation.shirt_number",
        ),
    )

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        shirt_number: int,
        row: int,
        column: int,
    ):
        """
        Initialize a new away team lineup association.

        :param match: Match entity for the lineup
        :param player: Player entity in the starting lineup
        :param shirt_number: Player's shirt number for the match
        :param row: Formation row position (1-based)
        :param column: Formation column position (1-based)
        """
        super().__init__(
            player_id=player.id,
            shirt_number=shirt_number,
            row=row,
            column=column,
        )
        self.match_id = match.id
