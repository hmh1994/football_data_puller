from datetime import datetime

from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.repository.entities.base import PulseliveEntity
from football_data_manager.repository.entities.competitions import CompetitionEntity

SEASONS_TABLE_NAME = "seasons"


class SeasonEntity(PulseliveEntity):
    """
    Entity model for football competition seasons.

    :ivar abbreviation: Season abbreviation code (e.g., '23/24')
    :ivar competition_id: Foreign key to the competition entity
    :ivar date_end: Season end date and time
    :ivar date_start: Season start date and time
    :ivar year_end: Season ending year
    :ivar year_start: Season starting year
    """

    __tablename__ = SEASONS_TABLE_NAME

    abbreviation: Mapped[str] = mapped_column(String, nullable=False)
    competition_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(CompetitionEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    date_end: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    date_start: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    year_end: Mapped[int] = mapped_column(Integer, nullable=False)
    year_start: Mapped[int] = mapped_column(Integer, nullable=False)

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

        :param abbreviation: Season abbreviation code (e.g., '23/24')
        :param competition: Competition entity this season belongs to
        :param date_end: Season end date and time
        :param date_start: Season start date and time
        :param season_source_id: Unique identifier from the source system
        :param year_end: Season ending year
        :param year_start: Season starting year
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
        Generate a unique source ID for the season entity.

        :param competition: Competition entity this season belongs to
        :param season_source_id: Unique identifier from the source system
        :returns: Combined source ID string
        """
        return f"{competition.source_id}_{season_source_id}"
