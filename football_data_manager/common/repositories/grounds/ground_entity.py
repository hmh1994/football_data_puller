from hashlib import md5

from sqlalchemy import Column, Double, Integer, String

from football_data_manager.common.repositories.constants import GROUNDS_TABLE_NAME
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)


class GroundEntity(PulseliveEntity):
    """
    Entity model for football grounds (stadiums/venues) with location and capacity information.

    Represents football stadiums and venues with multilingual names, geographic location,
    and facility details. Extends PulseliveEntity to inherit source tracking functionality.

    :ivar id: Unique identifier for the entity
    :ivar capacity: Stadium capacity (maximum number of spectators)
    :ivar city_name_en: City name in English where the ground is located
    :ivar city_name_kr: City name in Korean where the ground is located
    :ivar location_latitude: Geographic latitude coordinate of the ground
    :ivar location_longitude: Geographic longitude coordinate of the ground
    :ivar name_en: Ground name in English
    :ivar name_kr: Ground name in Korean
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = GROUNDS_TABLE_NAME

    capacity = Column(Integer, nullable=True)
    city_name_en = Column(String, nullable=False)
    city_name_kr = Column(String, nullable=False)
    location_latitude = Column(Double, nullable=True)
    location_longitude = Column(Double, nullable=True)
    name_en = Column(String, nullable=False, unique=True)
    name_kr = Column(String, nullable=False)

    def __init__(
        self,
        city_name_en: str,
        city_name_kr: str,
        name_en: str,
        name_kr: str,
        capacity: int | None = None,
        location_latitude: float | None = None,
        location_longitude: float | None = None,
    ) -> None:
        """
        Initialize a new ground entity.

        :param city_name_en: City name in English where the ground is located
        :param city_name_kr: City name in Korean where the ground is located
        :param name_en: Ground name in English
        :param name_kr: Ground name in Korean
        :param capacity: Stadium capacity (maximum number of spectators, optional)
        :param location_latitude: Geographic latitude coordinate of the ground (optional)
        :param location_longitude: Geographic longitude coordinate of the ground (optional)
        """
        super().__init__(source_id=self.get_source_id(name_en))
        self.capacity = capacity
        self.city_name_en = city_name_en
        self.city_name_kr = city_name_kr
        self.location_latitude = location_latitude
        self.location_longitude = location_longitude
        self.name_en = name_en
        self.name_kr = name_kr

    @staticmethod
    def get_source_id(name_en: str) -> str:
        """
        Generate a unique source ID for the ground entity.

        Creates a hash-based source ID from the English ground name to ensure
        uniqueness while maintaining deterministic ID generation.

        :param name_en: Name of the ground in English
        :returns: Unique source ID as a string
        """
        normal_name = name_en.replace(" ", "_").upper().encode("utf-8")
        hashed_name = md5(normal_name).hexdigest()
        return str(int(hashed_name, 16) % 2**16)
