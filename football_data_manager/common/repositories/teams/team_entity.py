from sqlalchemy import Column, String, Integer

from football_data_manager.common.repositories.constants import TEAMS_TABLE_NAME
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)


class TeamEntity(PulseliveEntity):
    """
    Entity model for football teams with localized names, icons, and championship associations.

    Represents football teams with multilingual names, visual branding elements, and
    championship season tracking. Contains both full names and abbreviated versions
    for different display contexts. Manages team identity and historical achievements.
    Extends PulseliveEntity to inherit source tracking functionality.

    :ivar id: Unique identifier for the entity
    :ivar abbreviation: Team abbreviation code (e.g., 'MCI', 'LIV', 'ARS')
    :ivar championship_season_associations: List of championship season associations
    :ivar founded_year: Year the team was founded (optional)
    :ivar icon_url: URL to team icon/logo image (optional)
    :ivar name_en: Team name in English
    :ivar name_kr: Team name in Korean
    :ivar short_name_en: Abbreviated team name in English
    :ivar short_name_kr: Abbreviated team name in Korean
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = TEAMS_TABLE_NAME

    abbreviation = Column(String, nullable=False, unique=True)
    founded_year = Column(Integer, nullable=True)
    icon_url = Column(String, nullable=True)
    name_en = Column(String, nullable=False)
    name_kr = Column(String, nullable=False)
    short_name_en = Column(String, nullable=False)
    short_name_kr = Column(String, nullable=False)

    def __init__(
        self,
        abbreviation: str,
        icon_url: str,
        name_en: str,
        name_kr: str,
        short_name_en: str,
        short_name_kr: str,
        source_id: str,
    ) -> None:
        """
        Initialize a new team entity.

        Creates a team with multilingual names, branding elements, and identification codes.
        Both full names and short names are required for different display contexts.

        :param abbreviation: Team abbreviation code (e.g., 'MCI', 'LIV', 'ARS')
        :param icon_url: URL to team icon/logo image
        :param name_en: Full team name in English
        :param name_kr: Full team name in Korean
        :param short_name_en: Abbreviated team name in English
        :param short_name_kr: Abbreviated team name in Korean
        :param source_id: Unique identifier from the source system
        """
        super().__init__(source_id=source_id)
        self.abbreviation = abbreviation
        self.championship_season_associations = []
        self.icon_url = icon_url
        self.name_en = name_en
        self.name_kr = name_kr
        self.short_name_en = short_name_en
        self.short_name_kr = short_name_kr
