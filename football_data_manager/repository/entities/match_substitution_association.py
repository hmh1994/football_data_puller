from sqlalchemy import String, ForeignKey, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.players import PlayerEntity

MATCH_SUBSTITUTION_ASSOCIATION_TABLE_NAME = "match_substitution_association"


class MatchSubstitutionAssociation(Base):
    """
    Association class for match substitutions.

    :ivar match_id: Foreign key to the match entity
    :ivar in_player_id: Foreign key to the player coming in
    :ivar out_player_id: Foreign key to the player going out
    :ivar clock: Time in minutes when the substitution occurred
    :ivar is_home: Flag indicating if the substitution is for the home team
    """

    __tablename__ = MATCH_SUBSTITUTION_ASSOCIATION_TABLE_NAME

    SUBSTITUTION_COLLECTION_NAME = "substitution_associations"

    match_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    in_player_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    out_player_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    clock: Mapped[int] = mapped_column(Integer, nullable=False)
    is_home: Mapped[bool] = mapped_column(Boolean, nullable=False, primary_key=True)

    match = relationship(
        "MatchEntity",
        backref=backref(
            name=SUBSTITUTION_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="MatchSubstitutionAssociation.clock",
        ),
    )

    def __init__(
        self,
        match: MatchEntity,
        in_player: PlayerEntity,
        out_player: PlayerEntity,
        clock: int,
        is_home: bool,
    ):
        """
        Initialize a new substitution association.

        :param match: Match entity where the substitution occurred
        :param in_player: Player entity coming into the match
        :param out_player: Player entity being substituted out
        :param clock: Time in minutes when the substitution occurred
        :param is_home: Whether the substitution is for the home team
        """
        super().__init__()
        self.match_id = match.id
        self.in_player_id = in_player.id
        self.out_player_id = out_player.id
        self.clock = clock
        self.is_home = is_home
