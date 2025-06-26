from datetime import datetime

from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship

from football_data_manager.common.new_repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.new_repositories.seasons.season_entity import (
    SeasonEntity,
)


class AwardEntity(PulseliveEntity):
    """
    Award entity model.
    :ivar id: Unique identifier for the award.
    :ivar season_id: Season ID associated with the award.
    :ivar source: Source of the entity data, set to PULSELIVE.
    :ivar source_id: Unique identifier from the source (`{team_id}_{season_id}_{player_id}`).
    :param date: Date of the award.
    :param description_en: Award description in English.
    :param description_kr: Award description in Korean.
    :param key: Unique key for the award.
    :param name_en: Award name in English.
    :param name_kr: Award name in Korean.
    :param icon_url: URL of the award icon.
    :param season: Season entity associated with the award.
    """

    __tablename__ = "awards_new"

    date = Column(DateTime, nullable=False)
    description_en = Column(String, nullable=True)
    description_kr = Column(String, nullable=True)
    name_en = Column(String, nullable=False)
    name_kr = Column(String, nullable=False)
    icon_url = Column(String, nullable=True)
    season_id = Column(String, nullable=False)
    season = relationship(SeasonEntity, lazy="joined", foreign_keys=season_id)

    def __init__(
        self,
        date: datetime,
        name_en: str,
        name_kr: str,
        season: SeasonEntity,
        description_en: str | None = None,
        description_kr: str | None = None,
        icon_url: str | None = None,
    ):
        super().__init__(source_id=self.get_source_id(season, name_en, date))
        self.date = date
        self.name_en = name_en
        self.name_kr = name_kr
        self.description_en = description_en
        self.description_kr = description_kr
        self.icon_url = icon_url
        self.season_id = season.id
        self.season = season

    @staticmethod
    def get_source_id(season: SeasonEntity, name_en: str, date: datetime) -> str:
        """
        Generate a unique source ID for the award based on the season and award details.
        :param season: Season entity.
        :param name_en: Name of the award in English.
        :param date: Date of the award.
        :return: Unique source ID.
        """
        return f"{season.source_id}_{name_en.replace(' ', '_').upper()}_{date.strftime('%y%m%d')}"
