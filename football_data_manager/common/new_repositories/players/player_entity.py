from datetime import datetime

from sqlalchemy import Column, String, Integer, CHAR, DateTime
from sqlalchemy.ext.associationproxy import association_proxy

from football_data_manager.common.new_repositories.constants import PLAYERS_TABLE_NAME
from football_data_manager.common.new_repositories.players.player_championship_association import (
    PlayerChampionshipAssociation,
)
from football_data_manager.common.new_repositories.pulselive_entity import (
    PulseliveEntity,
)


class PlayerEntity(PulseliveEntity):
    """
    Player entity model.
    :ivar id: Unique identifier for the player.
    :ivar championship_seasons: List of championship seasons entities related to the player.
    :ivar source: Source of the entity data, set to PULSELIVE.
    :param birth_country_en: Birth country in English.
    :param birth_country_kr: Birth country in Korean.
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

    __tablename__ = PLAYERS_TABLE_NAME

    birth_country_en = Column(String, nullable=False)
    birth_country_kr = Column(String, nullable=False)
    birth_date = Column(DateTime, nullable=False)
    birth_country_flag_icon_url = Column(String, nullable=False)
    birth_place = Column(String, nullable=True)
    championship_seasons = association_proxy(
        target_collection=PlayerChampionshipAssociation.SEASON_COLLECTION_NAME,
        attr=PlayerChampionshipAssociation.SEASON_ATTRIBUTE_NAME,
        create=lambda season: PlayerChampionshipAssociation(season=season, date_end=season.date_end),  # type: ignore[arg-type]
    )
    display_name_en = Column(String, nullable=False)
    display_name_kr = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    height = Column(Integer, nullable=True)
    national_team = Column(String, nullable=True)
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
        birth_place: str = None,
        height: int = None,
        national_team: str = None,
        photo_url: str = None,
        weight: int = None,
    ) -> None:
        super().__init__(source_id=source_id)
        self.birth_country_en = birth_country_en
        self.birth_country_kr = birth_country_kr
        self.birth_date = birth_date
        self.birth_country_flag_icon_url = birth_country_flag_icon_url
        self.display_name_en = display_name_en
        self.display_name_kr = display_name_kr
        self.full_name = full_name
        self.position = position
        self.position_info_en = position_info_en
        self.position_info_kr = position_info_kr
        self.birth_place = birth_place
        self.height = height
        self.national_team = national_team
        self.photo_url = photo_url
        self.weight = weight
