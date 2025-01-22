from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from football_data_puller.repositories import Base
from football_data_puller.repositories.grounds.ground_entity import GroundEntity


class TeamEntity(Base):
    """
    Team entity model.
    :param id: Team ID.
    :param abbreviation: Team abbreviation.
    :param ground_id: Ground ID.
    :param ground: Ground entity.
    :param icon_url: Team icon URL.
    :param name_en: Team name in English.
    :param name_kr: Team name in Korean.
    :param short_name_en: Team short name in English.
    :param short_name_kr: Team short name in Korean.
    """

    __tablename__ = "teams"

    id = Column(String, primary_key=True)
    abbreviation = Column(String)
    ground_id = Column(String, ForeignKey(GroundEntity.id))
    ground = relationship(GroundEntity, lazy="joined", foreign_keys=[ground_id])
    icon_url = Column(String, nullable=True)
    name_en = Column(String)
    name_kr = Column(String, nullable=True)
    short_name_en = Column(String)
    short_name_kr = Column(String, nullable=True)
