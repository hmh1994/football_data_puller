from sqlalchemy import Column, String

from football_data_manager.common.repositories.constants import (
    COMPETITIONS_TABLE_NAME,
)
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)


class CompetitionEntity(PulseliveEntity):
    """
    Entity model for football competitions with multilingual information.

    Represents football competitions and tournaments with localized names,
    descriptions, and icons. Extends PulseliveEntity to inherit source tracking functionality.

    :ivar id: Unique identifier for the entity
    :ivar abbreviation: Competition abbreviation (e.g., 'PL', 'UCL')
    :ivar description_en: Competition description in English
    :ivar description_kr: Competition description in Korean
    :ivar icon_url: URL to competition icon/logo image
    :ivar name_en: Competition name in English
    :ivar name_kr: Competition name in Korean
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = COMPETITIONS_TABLE_NAME

    abbreviation = Column(String, nullable=False, unique=True)
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
        """
        Initialize a new competition entity.

        :param abbreviation: Competition abbreviation (e.g., 'PL', 'UCL')
        :param name_en: Competition name in English
        :param name_kr: Competition name in Korean
        :param source_id: Unique identifier from the source system
        :param icon_url: URL to competition icon/logo image (optional)
        :param description_en: Competition description in English (optional)
        :param description_kr: Competition description in Korean (optional)
        """
        super().__init__(source_id=source_id)
        self.abbreviation = abbreviation
        self.name_en = name_en
        self.name_kr = name_kr
        self.icon_url = icon_url
        self.description_en = description_en
        self.description_kr = description_kr
