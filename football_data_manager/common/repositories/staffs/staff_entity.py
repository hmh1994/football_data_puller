from sqlalchemy import Column, String, Index

from football_data_manager.common.repositories.constants import STAFFS_TABLE_NAME
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)


class StaffEntity(PulseliveEntity):
    """
    Entity model for football coaching staff and management personnel with multilingual names.

    Represents football team staff including coaches, managers, assistants, and other personnel
    with display names in multiple languages and full legal names. Used for tracking
    coaching staff changes and team management throughout seasons.
    Extends PulseliveEntity to inherit source tracking functionality.

    :ivar id: Unique identifier for the entity
    :ivar display_name_en: Staff member's display name in English
    :ivar display_name_kr: Staff member's display name in Korean
    :ivar full_name: Staff member's full legal name
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = STAFFS_TABLE_NAME

    display_name_en = Column(String, nullable=False, unique=True)
    display_name_kr = Column(String, nullable=False)
    full_name = Column(String, nullable=False)

    __table_args__ = (Index("ix_staff_display_name_en", display_name_en),)

    def __init__(
        self, display_name_en: str, display_name_kr: str, full_name: str, source_id: str
    ) -> None:
        """
        Initialize a new staff entity.

        Creates a staff member with multilingual display names and full legal name.
        All names are required for proper identification and localization.

        :param display_name_en: Staff member's display name in English
        :param display_name_kr: Staff member's display name in Korean
        :param full_name: Staff member's full legal name
        :param source_id: Unique identifier from the source system
        """
        super().__init__(source_id=source_id)
        self.display_name_en = display_name_en
        self.display_name_kr = display_name_kr
        self.full_name = full_name
