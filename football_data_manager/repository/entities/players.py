from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.enums.side_enum import SideEnum
from football_data_manager.repository.entities.base import PulseliveEntity

PLAYERS_TABLE_NAME = "players"


class PlayerEntity(PulseliveEntity):
    """
    Entity model for football players with personal information.

    :ivar birth_country: Birth country name in English
    :ivar birth_date: Player's date of birth
    :ivar championship_season_associations: List of championship season associations
    :ivar display_name_en: Player display name in English
    :ivar display_name_kr: Player display name in Korean
    :ivar full_name: Player's full legal name
    :ivar height: Player height in centimeters (optional)
    :ivar nationality_en: Nationality in English
    :ivar nationality_kr: Nationality in Korean
    :ivar nationality_flag_icon_url: URL to nationality flag icon (optional)
    :ivar photo_url: URL to player photo
    :ivar position: Player position code
    :ivar preferred_foot: Player's preferred foot
    :ivar weight: Player weight in kilograms (optional)
    """

    __tablename__ = PLAYERS_TABLE_NAME

    birth_country: Mapped[str | None] = mapped_column(String, nullable=True)
    birth_date: Mapped[DateTime | None] = mapped_column(DateTime, nullable=True)
    display_name_en: Mapped[str] = mapped_column(String, nullable=False)
    display_name_kr: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nationality_en: Mapped[str] = mapped_column(String, nullable=False)
    nationality_kr: Mapped[str] = mapped_column(String, nullable=False)
    nationality_flag_icon_url: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    photo_url: Mapped[str | None] = mapped_column(String, nullable=True)
    position: Mapped[PositionEnum] = mapped_column(
        Enum(PositionEnum), nullable=False
    )
    preferred_foot: Mapped[SideEnum] = mapped_column(Enum(SideEnum), nullable=False)
    weight: Mapped[int | None] = mapped_column(Integer, nullable=True)

    def __init__(
        self,
        birth_country: str | None,
        birth_date: datetime | None,
        display_name_en: str,
        display_name_kr: str,
        full_name: str,
        nationality_en: str,
        nationality_kr: str,
        position: PositionEnum,
        preferred_foot: SideEnum,
        source_id: str,
        height: int | None = None,
        nationality_flag_icon_url: str | None = None,
        photo_url: str | None = None,
        weight: int | None = None,
    ) -> None:
        """
        Initialize a new player entity.

        :param birth_country: Birth country name in English
        :param birth_date: Player's date of birth (optional)
        :param display_name_en: Player display name in English
        :param display_name_kr: Player display name in Korean
        :param full_name: Player's full legal name
        :param nationality_en: Nationality in English
        :param nationality_kr: Nationality in Korean
        :param position: Player position
        :param preferred_foot: Player's preferred foot
        :param source_id: Unique identifier from the source system
        :param height: Player height in centimeters (optional)
        :param nationality_flag_icon_url: URL to nationality flag icon (optional)
        :param photo_url: URL to player photo (optional)
        :param weight: Player weight in kilograms (optional)
        """
        super().__init__(source_id=source_id)
        self.birth_country = birth_country
        self.birth_date = birth_date
        self.championship_season_associations = []
        self.display_name_en = display_name_en
        self.display_name_kr = display_name_kr
        self.full_name = full_name
        self.nationality_en = nationality_en
        self.nationality_kr = nationality_kr
        self.position = position
        self.preferred_foot = preferred_foot
        self.height = height
        self.nationality_flag_icon_url = nationality_flag_icon_url
        self.photo_url = photo_url
        self.weight = weight
