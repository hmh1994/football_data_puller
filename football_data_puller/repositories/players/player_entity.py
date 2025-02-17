from sqlalchemy import Column, String, ForeignKey, Integer, CHAR, Boolean, DateTime
from sqlalchemy.orm import relationship

from football_data_puller.repositories import Base
from football_data_puller.repositories.teams.team_entity import TeamEntity


class PlayerEntity(Base):
    """
    Player entity model.
    :param id: Player ID.
    :param birth_country: Player birth country.
    :param birth_date: Player birthdate.
    :param birth_place: Player birthplace.
    :param current_team_id: Current team ID.
    :param current_team: Current team entity.
    :param display_name_en: Player display name in English.
    :param display_name_kr: Player display name in Korean.
    :param full_name: Player full name.
    :param height: Player height.
    :param loan: Player loan status.
    :param national_team: Player national team.
    :param number: Player number.
    :param photo_url: Player photo URL.
    :param position: Player position.
    :param position_info_en: Player position info in English.
    :param position_info_kr: Player position info in Korean.
    :param weight: Player weight.
    """

    __tablename__ = "players"

    id = Column(String, primary_key=True)
    birth_country = Column(String)
    birth_date = Column(DateTime)
    birth_place = Column(String)
    current_team_id = Column(String, ForeignKey(TeamEntity.id))
    current_team = relationship(
        TeamEntity, lazy="joined", foreign_keys=[current_team_id]
    )
    display_name_en = Column(String)
    display_name_kr = Column(String, nullable=True)
    full_name = Column(String)
    height = Column(Integer)
    loan = Column(Boolean, nullable=True)
    national_team = Column(String, nullable=True)
    number = Column(Integer)
    photo_url = Column(String, nullable=True)
    position = Column(CHAR)
    position_info_en = Column(String)
    position_info_kr = Column(String, nullable=True)
    weight = Column(Integer)
