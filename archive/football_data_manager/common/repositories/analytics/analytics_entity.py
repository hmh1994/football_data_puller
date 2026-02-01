from sqlalchemy import Column, String, Float, Enum, ForeignKey

from football_data_manager.common.enums.analytics_key_enum import AnalyticsKeyEnum
from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.repositories.base_entity import BaseEntity
from football_data_manager.common.repositories.constants import ANALYTICS_TABLE_NAME
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity


class AnalyticsEntity(BaseEntity):
    """
    Entity model for analytics metrics associated with a season.

    Stores key-value analytics data with optional delta and description fields.
    Each analytics record is linked to a specific season for temporal context.

    :ivar id: Unique identifier for the entity
    :ivar key: Analytics metric key from AnalyticsKeyEnum
    :ivar title_en: Display title for the metric in English
    :ivar title_kr: Display title for the metric in Korean
    :ivar value: Current value of the metric
    :ivar delta: Change in value compared to previous period
    :ivar description_en: Optional description of the metric in English
    :ivar description_kr: Optional description of the metric in Korean
    :ivar season_id: Foreign key to the season entity
    :ivar source: Source of the entity data
    :ivar source_id: Unique identifier from the source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = ANALYTICS_TABLE_NAME

    key = Column(Enum(AnalyticsKeyEnum), nullable=False)
    title_en = Column(String, nullable=False)
    title_kr = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    delta = Column(Float, nullable=True)
    description_en = Column(String, nullable=True)
    description_kr = Column(String, nullable=True)
    season_id = Column(
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
        :param title_en: Display title for the metric in English
        :param title_kr: Display title for the metric in Korean
        :param value: Current value of the metric
        :param season: Season entity this analytics belongs to
        :param source: Source of the entity data
        :param source_id: Unique identifier from the source system
        :param delta: Change in value compared to previous period
        :param description_en: Optional description of the metric in English
        :param description_kr: Optional description of the metric in Korean
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