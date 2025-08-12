from hashlib import md5

from sqlalchemy import Column, String

from football_data_manager.common.repositories.constants import OFFICIALS_TABLE_NAME
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)


class OfficialEntity(PulseliveEntity):
    """
    Entity model for football officials (referees, assistants, VAR officials) with multilingual names.

    Represents football match officials with display names in multiple languages
    and full legal names. Extends PulseliveEntity to inherit source tracking functionality.

    :ivar id: Unique identifier for the entity
    :ivar display_name_en: Official's display name in English
    :ivar display_name_kr: Official's display name in Korean
    :ivar full_name: Official's full legal name
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = OFFICIALS_TABLE_NAME

    display_name_en = Column(String, nullable=False, unique=True)
    display_name_kr = Column(String, nullable=False)
    full_name = Column(String, nullable=False)

    def __init__(self, display_name_en: str, display_name_kr: str, full_name: str):
        """
        Initialize a new official entity.

        :param display_name_en: Official's display name in English
        :param display_name_kr: Official's display name in Korean
        :param full_name: Official's full legal name
        """
        super().__init__(source_id=self.get_source_id(display_name_en))
        self.display_name_en = display_name_en
        self.display_name_kr = display_name_kr
        self.full_name = full_name

    @staticmethod
    def get_source_id(display_name_en: str) -> str:
        """
        Generate a unique source ID for the official based on their display name.

        Creates a hash-based source ID from the English display name to ensure
        uniqueness while maintaining deterministic ID generation for officials.

        :param display_name_en: The displayed name of the official in English
        :returns: Unique source ID as a string
        """
        normal_name = display_name_en.encode("utf-8")
        hashed_name = md5(normal_name).hexdigest()
        return str(int(hashed_name, 16) % 2**16)
