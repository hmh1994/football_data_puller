from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.repository.entities.base import PulseliveEntity

COMPETITIONS_TABLE_NAME = "competitions"


class CompetitionEntity(PulseliveEntity):
    """
    Entity model for football competitions with multilingual information.

    :ivar abbreviation: Competition abbreviation (e.g., 'PL', 'UCL')
    :ivar description_en: Competition description in English
    :ivar description_kr: Competition description in Korean
    :ivar icon_url: URL to competition icon/logo image
    :ivar name_en: Competition name in English
    :ivar name_kr: Competition name in Korean
    """

    __tablename__ = COMPETITIONS_TABLE_NAME

    abbreviation: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description_en: Mapped[str | None] = mapped_column(String, nullable=True)
    description_kr: Mapped[str | None] = mapped_column(String, nullable=True)
    icon_url: Mapped[str | None] = mapped_column(String, nullable=True)
    name_en: Mapped[str] = mapped_column(String, nullable=False)
    name_kr: Mapped[str] = mapped_column(String, nullable=False)

    def __init__(
        self,
        abbreviation: str,
        name_en: str,
        name_kr: str,
        source_id: str,
        icon_url: str | None = None,
        description_en: str | None = None,
        description_kr: str | None = None,
    ):
        """
        Initialize a new competition entity.

        :param abbreviation: Competition abbreviation (e.g., 'PL', 'UCL')
        :param name_en: Competition name in English
        :param name_kr: Competition name in Korean
        :param source_id: Unique identifier from the source system
        :param icon_url: URL to competition icon/logo image (optional)
        :param description_en: Competition description in English (optional)
        :param description_kr: Competition description in Korean (optional)
        """
        super().__init__(source_id=source_id)
        self.abbreviation = abbreviation
        self.name_en = name_en
        self.name_kr = name_kr
        self.icon_url = icon_url
        self.description_en = description_en
        self.description_kr = description_kr
