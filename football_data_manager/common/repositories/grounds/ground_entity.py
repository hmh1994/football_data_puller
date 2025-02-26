from sqlalchemy import Column, Double, Integer, String

from football_data_manager.common.repositories import Base


class GroundEntity(Base):
    """
    Ground entity model.
    :param id: Ground ID.
    :param capacity: Ground capacity.
    :param city_name_en: City name in English.
    :param city_name_kr: City name in Korean.
    :param location_latitude: Ground location latitude.
    :param location_longitude: Ground location longitude.
    :param name_en: Ground name in English.
    :param name_kr: Ground name in Korean.
    """

    __tablename__ = "grounds"

    id = Column(String, primary_key=True)
    capacity = Column(Integer, nullable=True)
    city_name_en = Column(String)
    city_name_kr = Column(String, nullable=True)
    location_latitude = Column(Double, nullable=True)
    location_longitude = Column(Double, nullable=True)
    name_en = Column(String)
    name_kr = Column(String, nullable=True)

    @staticmethod
    def get_id(pulselive_id: int) -> str:
        """
        Get the ID of the ground.
        :param pulselive_id: Pulselive ID.
        :return: Ground ID.
        """
        return f"PULSELIVE_GROUND_{pulselive_id}"

    @property
    def pulselive_id(self) -> int:
        """
        Get the Pulselive ID of the ground.
        :return: Pulselive ID.
        """
        return int(self.id.removeprefix("PULSELIVE_GROUND_"))
