from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from football_data_puller.repositories import Base
from football_data_puller.repositories.competitions.competition_entity import (
    CompetitionEntity,
)


class SeasonEntity(Base):
    """
    Season entity model.
    :param id: Season ID.
    :param abbreviation: Season abbreviation.
    :param competition_id: Competition ID.
    :param competition: Competition entity.
    :param date_end: Season ends date.
    :param date_start: Season starts date.
    :param year_end: Season ends year.
    :param year_start: Season starts year.
    """

    __tablename__ = "seasons"

    id = Column(String, primary_key=True)
    abbreviation = Column(String)
    competition_id = Column(String, ForeignKey(CompetitionEntity.id))
    competition = relationship(
        CompetitionEntity, lazy="joined", foreign_keys=[competition_id]
    )
    date_end = Column(DateTime)
    date_start = Column(DateTime)
    year_end = Column(Integer)
    year_start = Column(Integer)
