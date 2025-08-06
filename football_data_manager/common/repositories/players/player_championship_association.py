from datetime import datetime

from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.constants import (
    PLAYER_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity


class PlayerChampionshipAssociation(Base):
    """
    Concrete association class for player championship relationships.

    Associates players with championship seasons they participated in,
    extending AbstractPlayerChampionshipAssociation with concrete table mapping and relationships.
    Tracks the end date of each championship for ordering purposes.

    :ivar season_id: Foreign key to the season entity
    :ivar date_end: End date of the championship season
    :ivar player_id: Foreign key to the player entity
    """

    __tablename__ = PLAYER_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME

    SEASON_COLLECTION_NAME = "championship_season_associations"

    season_id = Column(
        String,
        ForeignKey(SeasonEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        primary_key=True,
    )
    date_end = Column(DateTime, nullable=False)
    player = relationship(
        PlayerEntity,
        backref=backref(
            name=SEASON_COLLECTION_NAME,
            lazy="noload",
            cascade="all, delete-orphan",
            order_by="PlayerChampionshipAssociation.date_end",
        ),
    )

    def __init__(self, player: PlayerEntity, season: SeasonEntity, date_end: datetime):
        """
        Initialize a new player championship association.

        Creates an association between a player and a championship season,
        accepting entity objects and extracting IDs automatically.

        :param player: Player entity participating in the championship
        :param season: Season entity for the championship
        :param date_end: End date of the championship season
        """
        super().__init__()
        self.season_id = season.id
        self.date_end = date_end
        self.player_id = player.id
