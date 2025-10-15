from hashlib import md5

from sqlalchemy import Column, String, Enum

from football_data_manager.common.enums.award_type_enum import AwardTypeEnum
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
    :ivar type: Award type enum value (e.g., POTM, MOTM, GOTM)
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
    name_en = Column(String, nullable=True)
    name_kr = Column(String, nullable=True)
    type = Column(Enum(AwardTypeEnum), nullable=False)

    def __init__(
        self,
        _type: AwardTypeEnum,
        name_en: str | None = None,
        name_kr: str | None = None,
        description_en: str | None = None,
        description_kr: str | None = None,
        icon_url: str | None = None,
    ):
        """
        Initialize a new award entity.

        :param _type: Award type enum value
        :param name_en: Award type name in English (optional)
        :param name_kr: Award type name in Korean (optional)
        :param description_en: Award type description in English (optional)
        :param description_kr: Award type description in Korean (optional)
        :param icon_url: URL of the award type icon (optional)
        """
        super().__init__(source_id=self.get_source_id(_type))
        self.type = _type
        self.name_en = name_en
        self.name_kr = name_kr
        self.description_en = description_en
        self.description_kr = description_kr
        self.icon_url = icon_url

    @staticmethod
    def get_source_id(_type: AwardTypeEnum) -> str:
        """
        Generate a unique source ID for the award based on its type.

        Creates a hash-based source ID from the award type enum value to ensure
        uniqueness while maintaining deterministic ID generation for awards.

        :param _type: The award type enum value
        :returns: Unique source ID as a string
        """
        type_value = _type.value.encode("utf-8")
        hashed_type = md5(type_value).hexdigest()
        return str(int(hashed_type, 16) % 2**16)
