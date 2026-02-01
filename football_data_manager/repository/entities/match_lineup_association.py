from sqlalchemy import String, ForeignKey, Integer, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.players import PlayerEntity

MATCH_LINEUP_ASSOCIATION_TABLE_NAME = "match_lineup_association"


class MatchLineupAssociation(Base):
    """
    Association class for match lineup positions.

    :ivar match_id: Foreign key to the match entity
    :ivar player_id: Foreign key to the player in the lineup
    :ivar position: Player's position in the formation
    :ivar shirt_number: Player's shirt number
    :ivar row: Formation row position
    :ivar column: Formation column position
    :ivar is_home: Flag indicating if the player is in the home team lineup
    """

    __tablename__ = MATCH_LINEUP_ASSOCIATION_TABLE_NAME

    POSITION_COLLECTION_NAME = "lineup_associations"

    match_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    match = relationship(
        "MatchEntity",
        backref=backref(
            name=POSITION_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="MatchLineupAssociation.shirt_number",
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
    row: Mapped[int] = mapped_column(Integer, nullable=False)
    column: Mapped[int] = mapped_column(Integer, nullable=False)
    is_home: Mapped[bool] = mapped_column(Boolean, nullable=False, primary_key=True)

    def __init__(
        self,
        match: MatchEntity,
        player: PlayerEntity,
        position: PositionEnum,
        shirt_number: int,
        row: int,
        column: int,
        is_home: bool,
    ):
        """
        Initialize a new lineup association.

        :param match: Match entity for the lineup
        :param player: Player entity in the starting lineup
        :param position: Player's position in the formation
        :param shirt_number: Player's shirt number
        :param row: Formation row position
        :param column: Formation column position
        :param is_home: Whether the player is in the home team lineup
        """
        super().__init__()
        self.match_id = match.id
        self.player_id = player.id
        self.position = position
        self.shirt_number = shirt_number
        self.row = row
        self.column = column
        self.is_home = is_home
