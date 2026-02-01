from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.repository.entities.base import PulseliveEntity

TEAMS_TABLE_NAME = "teams"


class TeamEntity(PulseliveEntity):
    """
    Entity model for football teams with localized names and championship associations.

    :ivar abbreviation: Team abbreviation code (e.g., 'MCI', 'LIV', 'ARS')
    :ivar championship_season_associations: List of championship season associations
    :ivar color_primary: Primary team color (optional)
    :ivar color_secondary: Secondary team color (optional)
    :ivar description_en: Team description in English (optional)
    :ivar description_kr: Team description in Korean (optional)
    :ivar founded_year: Year the team was founded (optional)
    :ivar icon_url: URL to team icon/logo image
    :ivar name_en: Team name in English
    :ivar name_kr: Team name in Korean
    :ivar short_name_en: Abbreviated team name in English
    :ivar short_name_kr: Abbreviated team name in Korean
    """

    __tablename__ = TEAMS_TABLE_NAME

    abbreviation: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    color_primary: Mapped[str | None] = mapped_column(String, nullable=True)
    color_secondary: Mapped[str | None] = mapped_column(String, nullable=True)
    description_en: Mapped[str | None] = mapped_column(String, nullable=True)
    description_kr: Mapped[str | None] = mapped_column(String, nullable=True)
    founded_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    icon_url: Mapped[str] = mapped_column(String, nullable=False)
    name_en: Mapped[str] = mapped_column(String, nullable=False)
    name_kr: Mapped[str] = mapped_column(String, nullable=False)
    short_name_en: Mapped[str] = mapped_column(String, nullable=False)
    short_name_kr: Mapped[str] = mapped_column(String, nullable=False)

    def __init__(
        self,
        abbreviation: str,
        icon_url: str,
        name_en: str,
        name_kr: str,
        short_name_en: str,
        short_name_kr: str,
        source_id: str,
        color_primary: str | None = None,
        color_secondary: str | None = None,
        description_en: str | None = None,
        description_kr: str | None = None,
    ) -> None:
        """
        Initialize a new team entity.

        :param abbreviation: Team abbreviation code (e.g., 'MCI', 'LIV', 'ARS')
        :param icon_url: URL to team icon/logo image
        :param name_en: Full team name in English
        :param name_kr: Full team name in Korean
        :param short_name_en: Abbreviated team name in English
        :param short_name_kr: Abbreviated team name in Korean
        :param source_id: Unique identifier from the source system
        :param color_primary: Primary team color (optional)
        :param color_secondary: Secondary team color (optional)
        :param description_en: Team description in English (optional)
        :param description_kr: Team description in Korean (optional)
        """
        super().__init__(source_id=source_id)
        self.abbreviation = abbreviation
        self.championship_season_associations = []
        self.color_primary = color_primary
        self.color_secondary = color_secondary
        self.description_en = description_en
        self.description_kr = description_kr
        self.icon_url = icon_url
        self.name_en = name_en
        self.name_kr = name_kr
        self.short_name_en = short_name_en
        self.short_name_kr = short_name_kr
