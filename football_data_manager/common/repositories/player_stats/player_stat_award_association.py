from datetime import datetime

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories.awards.award_entity import AwardEntity
from football_data_manager.common.repositories.constants import (
    PLAYER_STAT_AWARD_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.player_stats.player_stat_entity import (
    AbstractPlayerStatAwardAssociation,
    PlayerStatEntity,
)


class PlayerStatAwardAssociation(AbstractPlayerStatAwardAssociation):
    """
    Concrete association class for player stat awards.

    Associates awards with player statistics for specific seasons.
    Extends AbstractPlayerStatAwardAssociation with player stat relationship.

    :ivar award_id: Foreign key to the award entity
    :ivar award: Award entity being given
    :ivar date: Date when the award was given
    :ivar player_stat_id: Foreign key to the player stat entity
    :ivar player_stat: Associated player stat entity with backref to award collection
    """

    __tablename__ = PLAYER_STAT_AWARD_ASSOCIATION_TABLE_NAME

    AWARD_COLLECTION_NAME = "award_associations"

    player_stat_id = Column(String, ForeignKey(PlayerStatEntity.id), primary_key=True)
    player_stat = relationship(
        PlayerStatEntity,
        backref=backref(
            AWARD_COLLECTION_NAME,
            lazy="select",
            cascade="all, delete-orphan",
            order_by="PlayerStatAwardAssociation.date",
        ),
    )

    def __init__(
        self, player_stat: PlayerStatEntity, award: AwardEntity, date: datetime
    ):
        """
        Initialize a new player stat award association.

        :param player_stat: Player stat entity receiving the award
        :param award: Award entity being given
        :param date: Date when the award was given
        """
        super().__init__(award_id=award.id, date=date)
        self.player_stat_id = player_stat.id
