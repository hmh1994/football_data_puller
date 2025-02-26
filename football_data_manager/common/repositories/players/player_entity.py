from sqlalchemy import Column, String, Integer, CHAR, DateTime

from football_data_manager.common.repositories import Base


class PlayerEntity(Base):
    """
    Player entity model.
    :param id: Player ID.
    :param birth_country: Player birth country.
    :param birth_date: Player birthdate.
    :param birth_place: Player birthplace.
    :param display_name_en: Player display name in English.
    :param display_name_kr: Player display name in Korean.
    :param full_name: Player full name.
    :param height: Player height.
    :param national_team: Player national team.
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
    birth_place = Column(String, nullable=True)
    display_name_en = Column(String)
    display_name_kr = Column(String, nullable=True)
    full_name = Column(String)
    height = Column(Integer, nullable=True)
    national_team = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    position = Column(CHAR)
    position_info_en = Column(String)
    position_info_kr = Column(String, nullable=True)
    weight = Column(Integer, nullable=True)

    @staticmethod
    def get_id(pulselive_id: int) -> str:
        """
        Get the ID of the player.
        :param pulselive_id: Pulselive ID.
        :return: Player ID.
        """
        return f"PULSELIVE_PLAYER_{pulselive_id}"

    @property
    def pulselive_id(self) -> int:
        """
        Get the Pulselive ID of the player.
        :return: Pulselive ID.
        """
        return int(self.id.removeprefix("PULSELIVE_PLAYER_"))
