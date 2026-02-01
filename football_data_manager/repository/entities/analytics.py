from sqlalchemy import String, Float, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.common.enums.analytics_key_enum import AnalyticsKeyEnum
from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.repository.entities.base import BaseEntity
from football_data_manager.repository.entities.seasons import SeasonEntity

ANALYTICS_TABLE_NAME = "analytics"


class AnalyticsEntity(BaseEntity):
    """
    Entity model for analytics metrics associated with a season.

    :ivar key: Analytics metric key from AnalyticsKeyEnum
    :ivar title_en: Display title for the metric in English
    :ivar title_kr: Display title for the metric in Korean
    :ivar value: Current value of the metric
    :ivar delta: Change in value compared to previous period
    :ivar description_en: Optional description in English
    :ivar description_kr: Optional description in Korean
    :ivar season_id: Foreign key to the season entity
    """

    __tablename__ = ANALYTICS_TABLE_NAME

    key: Mapped[AnalyticsKeyEnum] = mapped_column(
        Enum(AnalyticsKeyEnum), nullable=False
    )
    title_en: Mapped[str] = mapped_column(String, nullable=False)
    title_kr: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    delta: Mapped[float | None] = mapped_column(Float, nullable=True)
    description_en: Mapped[str | None] = mapped_column(String, nullable=True)
    description_kr: Mapped[str | None] = mapped_column(String, nullable=True)
    season_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(SeasonEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )

    def __init__(
        self,
        key: AnalyticsKeyEnum,
        title_en: str,
        title_kr: str,
        value: float,
        season: SeasonEntity,
        source: SourceEnum,
        source_id: str,
        delta: float | None = None,
        description_en: str | None = None,
        description_kr: str | None = None,
    ) -> None:
        """
        Initialize a new analytics entity.

        :param key: Analytics metric key from AnalyticsKeyEnum
        :param title_en: Display title in English
        :param title_kr: Display title in Korean
        :param value: Current value of the metric
        :param season: Season entity this analytics belongs to
        :param source: Source of the entity data
        :param source_id: Unique identifier from the source system
        :param delta: Change in value compared to previous period
        :param description_en: Optional description in English
        :param description_kr: Optional description in Korean
        """
        super().__init__(source=source, source_id=source_id)
        self.key = key
        self.title_en = title_en
        self.title_kr = title_kr
        self.value = value
        self.delta = delta
        self.description_en = description_en
        self.description_kr = description_kr
        self.season_id = season.id
