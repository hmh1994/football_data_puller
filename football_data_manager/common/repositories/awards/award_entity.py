from typing import Self

from sqlalchemy import Column, String, DateTime

from football_data_manager.common.repositories.pulselive_entity import PulseliveEntity


class AwardEntity(PulseliveEntity):
    """
    Award entity model.
    :ivar id: Unique identifier for the award.
    :ivar source: Source of the entity data, set to PULSELIVE.
    :param date: Date of the award.
    :param description_en: Award description in English.
    :param description_kr: Award description in Korean.
    :param name_en: Award name in English.
    :param name_kr: Award name in Korean.
    :param icon_url: URL of the award icon.
    :param source_id: Unique identifier from the source (`{team_id}_{season_id}_{player_id}`).
    """

    __tablename__ = "awards"

    date = Column(DateTime, nullable=False)
    description_en = Column(String, nullable=True)
    description_kr = Column(String, nullable=True)
    name_en = Column(String, nullable=False)
    name_kr = Column(String, nullable=False)
    icon_url = Column(String, nullable=True)

    def __init__(
        self,
        date: str,
        name_en: str,
        name_kr: str,
        source_id: str,
        description_en: str | None = None,
        description_kr: str | None = None,
        icon_url: str | None = None,
    ) -> Self:
        super().__init__(source_id=source_id)
        self.date = date
        self.name_en = name_en
        self.name_kr = name_kr
        self.description_en = description_en
        self.description_kr = description_kr
        self.icon_url = icon_url
