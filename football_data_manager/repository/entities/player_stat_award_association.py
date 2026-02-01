from datetime import datetime

from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.player_stats import PlayerStatEntity

PLAYER_STAT_AWARD_ASSOCIATION_TABLE_NAME = "player_stat_award_association"


class PlayerStatAwardAssociation(Base):
    """
    Association class for player stat awards.

    :ivar award_id: Foreign key to the award entity
    :ivar player_stat_id: Foreign key to the player stat entity
    :ivar date: Date when the award was given
    """

    __tablename__ = PLAYER_STAT_AWARD_ASSOCIATION_TABLE_NAME

    AWARD_COLLECTION_NAME = "award_associations"

    award_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("awards.id", ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    player_stat_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(PlayerStatEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    date: Mapped[DateTime] = mapped_column(DateTime, nullable=False, primary_key=True)
    player_stat = relationship(
        "PlayerStatEntity",
        backref=backref(
            name=AWARD_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="PlayerStatAwardAssociation.date",
        ),
    )

    def __init__(self, player_stat, award, date: datetime):
        """
        Initialize a new player stat award association.

        :param player_stat: Player stat entity receiving the award
        :param award: Award entity being given
        :param date: Date when the award was given
        """
        super().__init__()
        self.award_id = award.id
        self.date = date
        self.player_stat_id = player_stat.id
