from sqlalchemy import Column, String

from football_data_manager.common.old_repositories.pulselive_entity import (
    PulseliveEntity,
)


class CompetitionEntity(PulseliveEntity):
    """
    Competition entity model.
    :ivar id: Unique identifier for the entity.
    :ivar source: Source of the entity data, set to PULSELIVE.
    :param abbreviation: Competition abbreviation.
    :param description_en: Competition description in English.
    :param description_kr: Competition description in Korean.
    :param icon_url: Competition icon URL.
    :param name_en: Competition name in English.
    :param name_kr: Competition name in Korean.
    :param source_id: Unique identifier from the source.
    """

    __tablename__ = "competitions"

    abbreviation = Column(String, nullable=False)
    description_en = Column(String, nullable=True)
    description_kr = Column(String, nullable=True)
    icon_url = Column(String, nullable=True)
    name_en = Column(String, nullable=False)
    name_kr = Column(String, nullable=False)

    def __init__(
        self,
        abbreviation: str,
        name_en: str,
        name_kr: str,
        source_id: str,
        icon_url: str | None = None,
        description_en: str | None = None,
        description_kr: str | None = None,
    ):
        super().__init__(source_id=source_id)
        self.abbreviation = abbreviation
        self.name_en = name_en
        self.name_kr = name_kr
        self.icon_url = icon_url
        self.description_en = description_en
        self.description_kr = description_kr
