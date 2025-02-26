from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.competitions.competition_entity import (
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

    @staticmethod
    def get_id(pulselive_id: int) -> str:
        """
        Get the ID of the season.
        :param pulselive_id: Pulselive ID.
        :return: Season ID.
        """
        return f"PULSELIVE_SEASON_{pulselive_id}"

    @property
    def pulselive_id(self) -> int:
        """
        Get the Pulselive ID of the season.
        :return: Pulselive ID.
        """
        return int(self.id.removeprefix("PULSELIVE_SEASON_"))
