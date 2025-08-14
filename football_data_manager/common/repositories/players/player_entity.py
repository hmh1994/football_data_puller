from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Enum

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.enums.side_enum import SideEnum
from football_data_manager.common.repositories.constants import PLAYERS_TABLE_NAME
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)


class PlayerEntity(PulseliveEntity):
    """
    Entity model for football players with personal information and championship history.

    Represents football players with complete personal details including birth information,
    physical attributes, position data, and championship season associations.
    Extends PulseliveEntity to inherit source tracking functionality.

    :ivar id: Unique identifier for the entity
    :ivar birth_country: Birth country name in English
    :ivar birth_date: Player's date of birth
    :ivar championship_season_associations: List of championship season associations
    :ivar display_name_en: Player display name in English
    :ivar display_name_kr: Player display name in Korean
    :ivar full_name: Player's full legal name
    :ivar height: Player height in centimeters (optional)
    :ivar nationality_en: Nationality representation in English (optional)
    :ivar nationality_flag_icon_url: URL to birth country flag icon (optional)
    :ivar photo_url: URL to player photo
    :ivar position: Player position code
    :ivar weight: Player weight in kilograms (optional)
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = PLAYERS_TABLE_NAME

    birth_country = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    display_name_en = Column(String, nullable=False)
    display_name_kr = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    height = Column(Integer, nullable=True)
    nationality_en = Column(String, nullable=False)
    nationality_kr = Column(String, nullable=False)
    nationality_flag_icon_url = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    position = Column(Enum(PositionEnum), nullable=False)
    preferred_foot = Column(Enum(SideEnum), nullable=False)
    weight = Column(Integer, nullable=True)

    def __init__(
        self,
        birth_country: str | None,
        birth_date: datetime | None,
        display_name_en: str,
        display_name_kr: str,
        full_name: str,
        nationality_en: str,
        nationality_kr: str,
        position: PositionEnum,
        preferred_foot: SideEnum,
        source_id: str,
        height: int | None = None,
        nationality_flag_icon_url: str | None = None,
        photo_url: str | None = None,
        weight: int | None = None,
    ) -> None:
        """
        Initialize a new player entity.

        :param birth_country: Birth country name in English
        :param display_name_en: Player display name in English
        :param display_name_kr: Player display name in Korean
        :param full_name: Player's full legal name
        :param nationality_en: Nationality representation in English
        :param nationality_kr: Nationality representation in Korean
        :param position: Player position
        :param source_id: Unique identifier from the source system
        :param birth_date: Player's date of birth (optional)
        :param height: Player height in centimeters (optional)
        :param nationality_flag_icon_url: URL to birth country flag icon (optional)
        :param photo_url: URL to player photo (optional)
        :param weight: Player weight in kilograms (optional)
        """
        super().__init__(source_id=source_id)
        self.birth_country = birth_country
        self.birth_date = birth_date
        self.championship_season_associations = []
        self.display_name_en = display_name_en
        self.display_name_kr = display_name_kr
        self.full_name = full_name
        self.nationality_en = nationality_en
        self.nationality_kr = nationality_kr
        self.position = position
        self.preferred_foot = preferred_foot
        self.height = height
        self.nationality_flag_icon_url = nationality_flag_icon_url
        self.photo_url = photo_url
        self.weight = weight
