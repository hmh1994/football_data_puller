from sqlalchemy import Column, String

from football_data_manager.common.old_repositories.pulselive_entity import (
    PulseliveEntity,
)


class TeamEntity(PulseliveEntity):
    """
    Team entity model.
    :ivar id: Unique identifier for the entity.
    :ivar championship_season_ids: List of season IDs for championships related to the team.
    :ivar championship_seasons: List of championship seasons entities related to the team.
    :ivar source: Source of the entity data, set to PULSELIVE.
    :param abbreviation: Team abbreviation.
    :param icon_url: Team icon URL.
    :param name_en: Team name in English.
    :param name_kr: Team name in Korean.
    :param short_name_en: Team short name in English.
    :param short_name_kr: Team short name in Korean.
    :param source_id: Unique identifier from the source.
    """

    __tablename__ = "teams"

    abbreviation = Column(String, nullable=False)
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
        super().__init__(source_id=source_id)
        self.abbreviation = abbreviation
        self.icon_url = icon_url
        self.name_en = name_en
        self.name_kr = name_kr
        self.short_name_en = short_name_en
        self.short_name_kr = short_name_kr
