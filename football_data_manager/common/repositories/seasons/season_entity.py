from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.constants import SEASONS_TABLE_NAME
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)


class SeasonEntity(PulseliveEntity):
    """
    Entity model for football competition seasons with temporal and competition information.

    Represents football seasons with start/end dates, year boundaries, and competition associations.
    Contains seasonal abbreviations and temporal data for organizing matches and events.
    Extends PulseliveEntity to inherit source tracking functionality.

    :ivar id: Unique identifier for the entity
    :ivar abbreviation: Season abbreviation code (e.g., '23/24', '2023-2024')
    :ivar competition_id: Foreign key to the competition entity
    :ivar date_end: Season end date and time
    :ivar date_start: Season start date and time
    :ivar year_end: Season ending year as integer
    :ivar year_start: Season starting year as integer
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = SEASONS_TABLE_NAME

    abbreviation = Column(String, nullable=False)
    competition_id = Column(
        String,
        ForeignKey(CompetitionEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    date_end = Column(DateTime, nullable=False)
    date_start = Column(DateTime, nullable=False)
    year_end = Column(Integer, nullable=False)
    year_start = Column(Integer, nullable=False)

    def __init__(
        self,
        abbreviation: str,
        competition: CompetitionEntity,
        date_end: datetime,
        date_start: datetime,
        season_source_id: str,
        year_end: int,
        year_start: int,
    ) -> None:
        """
        Initialize a new season entity.

        Creates a season with temporal boundaries and competition association.
        Automatically extracts competition ID from the provided competition entity.

        :param abbreviation: Season abbreviation code (e.g., '23/24')
        :param competition: Competition entity this season belongs to
        :param date_end: Season end date and time
        :param date_start: Season start date and time
        :param season_source_id: Unique identifier from the source system
        :param year_end: Season ending year as integer
        :param year_start: Season starting year as integer
        """
        super().__init__(source_id=self.get_source_id(competition, season_source_id))
        self.abbreviation = abbreviation
        self.competition_id = competition.id
        self.date_end = date_end
        self.date_start = date_start
        self.year_end = year_end
        self.year_start = year_start

    @staticmethod
    def get_source_id(competition: CompetitionEntity, season_source_id: str) -> str:
        """
        Generate a unique source ID for the season entity based on competition and season ID.

        Combines competition source ID with the season ID to create a unique identifier
        for database operations.

        :param competition: Competition entity this season belongs to
        :param season_source_id: Unique identifier from the source system
        :returns: Combined source ID string
        """
        return f"{competition.source_id}_{season_source_id}"

