from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.grounds.ground_entity import GroundEntity


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
    ground_id = Column(String, ForeignKey(GroundEntity.id), nullable=True)
    ground = relationship(GroundEntity, lazy="joined", foreign_keys=[ground_id])
    icon_url = Column(String, nullable=True)
    name_en = Column(String)
    name_kr = Column(String, nullable=True)
    short_name_en = Column(String)
    short_name_kr = Column(String, nullable=True)

    @staticmethod
    def get_id(pulselive_id: int) -> str:
        """
        Get the ID of the team.
        :param pulselive_id: Pulselive ID.
        :return: Team ID.
        """
        return f"PULSELIVE_TEAM_{pulselive_id}"

    @property
    def pulselive_id(self) -> int:
        """
        Get the Pulselive ID of the team.
        :return: Pulselive ID.
        """
        return int(self.id.removeprefix("PULSELIVE_TEAM_"))
