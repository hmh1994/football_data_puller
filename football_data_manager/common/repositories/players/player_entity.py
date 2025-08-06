from datetime import datetime

from sqlalchemy import Column, String, Integer, CHAR, DateTime

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
    :ivar birth_country_en: Birth country name in English
    :ivar birth_country_kr: Birth country name in Korean
    :ivar birth_date: Player's date of birth
    :ivar birth_country_flag_icon_url: URL to birth country flag icon
    :ivar birth_place: Player's birthplace (optional)
    :ivar championship_season_associations: List of championship season associations
    :ivar display_name_en: Player display name in English
    :ivar display_name_kr: Player display name in Korean
    :ivar full_name: Player's full legal name
    :ivar height: Player height in centimeters (optional)
    :ivar nationality: Nationality representation (optional)
    :ivar photo_url: URL to player photo
    :ivar position: Player position code
    :ivar position_info_en: Player position description in English
    :ivar position_info_kr: Player position description in Korean
    :ivar weight: Player weight in kilograms (optional)
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = PLAYERS_TABLE_NAME

    birth_country_en = Column(String, nullable=False)
    birth_country_kr = Column(String, nullable=False)
    birth_date = Column(DateTime, nullable=False)
    birth_country_flag_icon_url = Column(String, nullable=False)
    birth_place = Column(String, nullable=True)
    display_name_en = Column(String, nullable=False)
    display_name_kr = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    height = Column(Integer, nullable=True)
    nationality = Column(String, nullable=True)
    photo_url = Column(String, nullable=False)
    position = Column(CHAR, nullable=False)
    position_info_en = Column(String, nullable=False)
    position_info_kr = Column(String, nullable=False)
    weight = Column(Integer, nullable=True)

    def __init__(
        self,
        birth_country_en: str,
        birth_country_kr: str,
        birth_date: datetime,
        birth_country_flag_icon_url: str,
        display_name_en: str,
        display_name_kr: str,
        full_name: str,
        position: str,
        position_info_en: str,
        position_info_kr: str,
        source_id: str,
        birth_place: str | None = None,
        height: int | None = None,
        nationality: str | None = None,
        photo_url: str | None = None,
        weight: int | None = None,
    ) -> None:
        """
        Initialize a new player entity.

        :param birth_country_en: Birth country name in English
        :param birth_country_kr: Birth country name in Korean
        :param birth_date: Player's date of birth
        :param birth_country_flag_icon_url: URL to birth country flag icon
        :param display_name_en: Player display name in English
        :param display_name_kr: Player display name in Korean
        :param full_name: Player's full legal name
        :param position: Player position code
        :param position_info_en: Player position description in English
        :param position_info_kr: Player position description in Korean
        :param source_id: Unique identifier from the source system
        :param birth_place: Player's birthplace (optional)
        :param height: Player height in centimeters (optional)
        :param nationality: Nationality representation (optional)
        :param photo_url: URL to player photo (optional)
        :param weight: Player weight in kilograms (optional)
        """
        super().__init__(source_id=source_id)
        self.birth_country_en = birth_country_en
        self.birth_country_kr = birth_country_kr
        self.birth_date = birth_date
        self.birth_country_flag_icon_url = birth_country_flag_icon_url
        self.championship_season_associations = []
        self.display_name_en = display_name_en
        self.display_name_kr = display_name_kr
        self.full_name = full_name
        self.position = position
        self.position_info_en = position_info_en
        self.position_info_kr = position_info_kr
        self.birth_place = birth_place
        self.height = height
        self.nationality = nationality
        self.photo_url = photo_url
        self.weight = weight
