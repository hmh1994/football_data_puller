from sqlalchemy import String, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.players import PlayerEntity

MATCH_SUBSTITUTE_ASSOCIATION_TABLE_NAME = "match_substitute_association"


class MatchSubstituteAssociation(Base):
    """
    Association class for match substitute players.

    :ivar match_id: Foreign key to the match entity
    :ivar player_id: Foreign key to the substitute player
    :ivar position: Player's position
    :ivar shirt_number: Player's shirt number
    :ivar is_home: Flag indicating if the substitute is for the home team
    """

    __tablename__ = MATCH_SUBSTITUTE_ASSOCIATION_TABLE_NAME

    PLAYER_INFO_COLLECTION_NAME = "substitute_associations"

    match_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    match = relationship(
        "MatchEntity",
        backref=backref(
            name=PLAYER_INFO_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="MatchSubstituteAssociation.shirt_number",
        ),
    )
    player_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    position: Mapped[PositionEnum] = mapped_column(
        Enum(PositionEnum), nullable=False
    )
    shirt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    is_home: Mapped[bool] = mapped_column(Boolean, nullable=False, primary_key=True)

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        position: PositionEnum,
        shirt_number: int,
        is_home: bool,
    ):
        """
        Initialize a new substitute association.

        :param match: Match entity for the substitute
        :param player: Player entity on the bench
        :param position: Player's position
        :param shirt_number: Player's shirt number
        :param is_home: Whether the substitute is for the home team
        """
        super().__init__()
        self.match_id = match.id
        self.player_id = player.id
        self.position = position
        self.shirt_number = shirt_number
        self.is_home = is_home
