from hashlib import md5

from sqlalchemy import Double, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.repository.entities.base import PulseliveEntity

GROUNDS_TABLE_NAME = "grounds"


class GroundEntity(PulseliveEntity):
    """
    Entity model for football grounds (stadiums/venues).

    :ivar capacity: Stadium capacity (maximum number of spectators)
    :ivar city_name_en: City name in English
    :ivar city_name_kr: City name in Korean
    :ivar location_latitude: Geographic latitude coordinate
    :ivar location_longitude: Geographic longitude coordinate
    :ivar name_en: Ground name in English
    :ivar name_kr: Ground name in Korean
    """

    __tablename__ = GROUNDS_TABLE_NAME

    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    city_name_en: Mapped[str] = mapped_column(String, nullable=False)
    city_name_kr: Mapped[str] = mapped_column(String, nullable=False)
    location_latitude: Mapped[float | None] = mapped_column(Double, nullable=True)
    location_longitude: Mapped[float | None] = mapped_column(Double, nullable=True)
    name_en: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    name_kr: Mapped[str] = mapped_column(String, nullable=False)

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

        :param city_name_en: City name in English
        :param city_name_kr: City name in Korean
        :param name_en: Ground name in English
        :param name_kr: Ground name in Korean
        :param capacity: Stadium capacity (optional)
        :param location_latitude: Geographic latitude (optional)
        :param location_longitude: Geographic longitude (optional)
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

        :param name_en: Name of the ground in English
        :returns: Unique source ID as a string
        """
        normal_name = name_en.replace(" ", "_").upper().encode("utf-8")
        hashed_name = md5(normal_name).hexdigest()
        return str(int(hashed_name, 16) % 2**16)
