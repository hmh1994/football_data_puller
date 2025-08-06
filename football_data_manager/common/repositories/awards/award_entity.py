from hashlib import md5

from sqlalchemy import Column, String, Index

from football_data_manager.common.repositories.constants import AWARDS_TABLE_NAME
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)


class AwardEntity(PulseliveEntity):
    """
    Entity model for football awards with multilingual information.

    Represents football awards and achievements with descriptions and icons.
    Extends PulseliveEntity to inherit source tracking functionality.

    :ivar id: Unique identifier for the award type
    :ivar description_en: Award type description in English
    :ivar description_kr: Award type description in Korean
    :ivar icon_url: URL of the award type icon
    :ivar name_en: Award type name in English
    :ivar name_kr: Award type name in Korean
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = AWARDS_TABLE_NAME

    description_en = Column(String, nullable=True)
    description_kr = Column(String, nullable=True)
    icon_url = Column(String, nullable=True)
    name_en = Column(String, nullable=False, unique=True)
    name_kr = Column(String, nullable=False)

    __table_args__ = (Index("ix_award_name_en", name_en),)

    def __init__(
        self,
        name_en: str,
        name_kr: str,
        description_en: str | None = None,
        description_kr: str | None = None,
        icon_url: str | None = None,
    ):
        """
        Initialize a new award entity.

        :param name_en: Award type name in English
        :param name_kr: Award type name in Korean
        :param description_en: Award type description in English (optional)
        :param description_kr: Award type description in Korean (optional)
        :param icon_url: URL of the award type icon (optional)
        """
        super().__init__(source_id=self.get_source_id(name_en))
        self.name_en = name_en
        self.name_kr = name_kr
        self.description_en = description_en
        self.description_kr = description_kr
        self.icon_url = icon_url

    @staticmethod
    def get_source_id(name_en: str) -> str:
        """
        Generate a unique source ID for the award entity.

        Creates a hash-based source ID from the English award name to ensure
        uniqueness while maintaining deterministic ID generation.

        :param name_en: Name of the award in English
        :returns: Unique source ID as a string
        """
        normal_name = name_en.replace(" ", "_").upper().encode("utf-8")
        hashed_name = md5(normal_name).hexdigest()
        return str(int(hashed_name, 16) % 2**16)
