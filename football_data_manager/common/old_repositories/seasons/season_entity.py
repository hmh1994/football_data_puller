from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from football_data_manager.common.old_repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.old_repositories.pulselive_entity import (
    PulseliveEntity,
)


class SeasonEntity(PulseliveEntity):
    """
    Season entity model.
    :ivar id: Unique identifier for the season.
    :ivar competition_id: Competition ID associated with the season.
    :ivar source: Source of the entity data, set to PULSELIVE.
    :param abbreviation: Season abbreviation.
    :param competition: Competition entity associated with the season.
    :param date_end: Season ends date.
    :param date_start: Season starts date.
    :param source_id: Unique identifier from the source.
    :param year_end: Season ends year.
    :param year_start: Season starts year.
    """

    __tablename__ = "seasons"

    abbreviation = Column(String, nullable=False)
    competition_id = Column(String, ForeignKey(CompetitionEntity.id), nullable=False)
    competition = relationship(
        CompetitionEntity, lazy="joined", foreign_keys=competition_id
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
        source_id: str,
        year_end: int,
        year_start: int,
    ) -> None:
        super().__init__(source_id=source_id)
        self.abbreviation = abbreviation
        self.competition_id = competition.id
        self.date_end = date_end
        self.date_start = date_start
        self.year_end = year_end
        self.year_start = year_start
