from datetime import datetime

from sqlalchemy import String, ARRAY, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.common.enums.news_type_enum import NewsTypeEnum
from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.repository.entities.base import BaseEntity

NEWS_TABLE_NAME = "news"


class NewsEntity(BaseEntity):
    """
    Entity model for news articles with multilingual content.

    :ivar author_en: List of authors in English
    :ivar author_kr: List of authors in Korean
    :ivar content_en: News content in English
    :ivar content_kr: News content in Korean
    :ivar publish_date: Date and time when the news was published
    :ivar url: URL of the news article
    :ivar thumbnail_url: URL of the news thumbnail image
    :ivar title_en: Title in English
    :ivar title_kr: Title in Korean
    :ivar type: Type of the news article
    """

    __tablename__ = NEWS_TABLE_NAME

    author_en: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    author_kr: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    content_en: Mapped[str] = mapped_column(String, nullable=False)
    content_kr: Mapped[str] = mapped_column(String, nullable=False)
    publish_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    url: Mapped[str] = mapped_column(String, nullable=False)
    thumbnail_url: Mapped[str] = mapped_column(String, nullable=False)
    title_en: Mapped[str] = mapped_column(String, nullable=False)
    title_kr: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[NewsTypeEnum] = mapped_column(Enum(NewsTypeEnum), nullable=False)

    def __init__(
        self,
        author_en: list[str],
        author_kr: list[str],
        content_en: str,
        content_kr: str,
        publish_date: datetime,
        url: str,
        source: SourceEnum,
        source_id: str,
        thumbnail_url: str,
        title_en: str,
        title_kr: str,
        typ: NewsTypeEnum,
    ):
        """
        Initialize a new news entity.

        :param author_en: List of authors in English
        :param author_kr: List of authors in Korean
        :param content_en: News content in English
        :param content_kr: News content in Korean
        :param publish_date: Publication date and time
        :param url: URL of the news article
        :param source: Source of the news article
        :param source_id: Unique identifier from the source
        :param thumbnail_url: URL of the news thumbnail image
        :param title_en: Title in English
        :param title_kr: Title in Korean
        :param typ: Type of the news article
        """
        super().__init__(source=source, source_id=source_id)
        self.author_en = author_en
        self.author_kr = author_kr
        self.content_en = content_en
        self.content_kr = content_kr
        self.team_associations = []
        self.publish_date = publish_date
        self.url = url
        self.thumbnail_url = thumbnail_url
        self.title_en = title_en
        self.title_kr = title_kr
        self.type = typ
