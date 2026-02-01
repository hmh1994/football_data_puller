from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.players import PlayerEntity

PLAYER_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME = "player_championship_association"


class PlayerChampionshipAssociation(Base):
    """
    Association class for player championship relationships.

    :ivar season_id: Foreign key to the season entity
    :ivar player_id: Foreign key to the player entity
    :ivar date_end: End date of the championship season
    """

    __tablename__ = PLAYER_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME

    SEASON_COLLECTION_NAME = "championship_season_associations"

    season_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("seasons.id", ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    player_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    date_end: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    player = relationship(
        PlayerEntity,
        backref=backref(
            name=SEASON_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="PlayerChampionshipAssociation.date_end",
        ),
    )

    def __init__(self, player, season, date_end: datetime):
        """
        Initialize a new player championship association.

        :param player: Player entity participating in the championship
        :param season: Season entity for the championship
        :param date_end: End date of the championship season
        """
        super().__init__()
        self.season_id = season.id
        self.date_end = date_end
        self.player_id = player.id
