from sqlalchemy import Column, Double, Integer, String

from football_data_manager.common.new_repositories.constants import GROUNDS_TABLE_NAME
from football_data_manager.common.new_repositories.pulselive_entity import (
    PulseliveEntity,
)


class GroundEntity(PulseliveEntity):
    """
    Entity model for the ground of a football match.
    :ivar id: Unique identifier for the entity.
    :ivar source: Source of the entity data, set to PULSELIVE.
    :param capacity: Ground capacity.
    :param city_name_en: City name in English.
    :param city_name_kr: City name in Korean.
    :param location_latitude: Ground location latitude.
    :param location_longitude: Ground location longitude.
    :param name_en: Ground name in English.
    :param name_kr: Ground name in Korean.
    :param source_id: Unique identifier from the source.
    """

    __tablename__ = GROUNDS_TABLE_NAME

    capacity = Column(Integer, nullable=True)
    city_name_en = Column(String, nullable=False)
    city_name_kr = Column(String, nullable=False)
    location_latitude = Column(Double, nullable=True)
    location_longitude = Column(Double, nullable=True)
    name_en = Column(String, nullable=False)
    name_kr = Column(String, nullable=False)

    def __init__(
        self,
        city_name_en: str,
        city_name_kr: str,
        name_en: str,
        name_kr: str,
        source_id: str,
        capacity: int | None = None,
        location_latitude: float | None = None,
        location_longitude: float | None = None,
    ) -> None:
        super().__init__(source_id=source_id)
        self.capacity = capacity
        self.city_name_en = city_name_en
        self.city_name_kr = city_name_kr
        self.location_latitude = location_latitude
        self.location_longitude = location_longitude
        self.name_en = name_en
        self.name_kr = name_kr
