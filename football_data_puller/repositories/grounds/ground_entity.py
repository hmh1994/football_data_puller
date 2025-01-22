from sqlalchemy import Column, Double, Integer, String

from football_data_puller.repositories import Base


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
    capacity = Column(Integer)
    city_name_en = Column(String)
    city_name_kr = Column(String, nullable=True)
    location_latitude = Column(Double)
    location_longitude = Column(Double)
    name_en = Column(String)
    name_kr = Column(String, nullable=True)
