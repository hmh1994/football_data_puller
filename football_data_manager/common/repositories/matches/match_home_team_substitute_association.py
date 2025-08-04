from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories.constants import (
    MATCH_HOME_TEAM_SUBSTITUTE_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
    AbstractMatchSubstituteAssociation,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)


class MatchHomeTeamSubstituteAssociation(AbstractMatchSubstituteAssociation):
    """
    Concrete association class for home team substitute players.

    Associates substitute players (bench) with their shirt numbers.
    Extends AbstractMatchSubstituteAssociation with match-specific relationship.

    :ivar match_id: Foreign key to the match entity
    :ivar match: Associated match entity with backref to substitute collection
    """

    __tablename__ = MATCH_HOME_TEAM_SUBSTITUTE_ASSOCIATION_TABLE_NAME

    PLAYER_INFO_COLLECTION_NAME = "home_team_substitute_associations"

    match_id = Column(String, ForeignKey(MatchEntity.id), primary_key=True)
    match = relationship(
        MatchEntity,
        backref=backref(
            PLAYER_INFO_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="MatchHomeTeamSubstituteAssociation.shirt_number",
        ),
    )

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        shirt_number: int,
    ):
        """
        Initialize a new home team substitute association.

        :param match: Match entity for the substitute
        :param player: Player entity on the substitute bench
        :param shirt_number: Player's shirt number for the match
        """
        super().__init__(player_id=player.id, shirt_number=shirt_number)
        self.match_id = match.id
