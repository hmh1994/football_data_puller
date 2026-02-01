from datetime import datetime

from sqlalchemy import Column, String, ARRAY, DateTime, Enum

from football_data_manager.common.enums.news_type_enum import NewsTypeEnum
from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.repositories.base_entity import BaseEntity
from football_data_manager.common.repositories.constants import NEWS_TABLE_NAME


class NewsEntity(BaseEntity):
    """
    Entity model for news articles with multilingual content and team associations.

    Represents news articles with content in multiple languages and
    associations to football teams mentioned in the articles.

    :ivar id: Unique identifier for the entity
    :ivar author_en: List of authors in English
    :ivar author_kr: List of authors in Korean
    :ivar content_en: News content in English
    :ivar content_kr: News content in Korean
    :ivar team_associations: List of teams mentioned in the news
    :ivar publish_date: Date and time when the news was published
    :ivar url: URL of the news article
    :ivar source: Source of the news article
    :ivar source_id: Unique identifier from the source
    :ivar thumbnail_url: URL of the news thumbnail image
    :ivar title_en: Title of the news in English
    :ivar title_kr: Title of the news in Korean
    :ivar type: Type of the news article
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = NEWS_TABLE_NAME

    author_en = Column(ARRAY(String), nullable=False)
    author_kr = Column(ARRAY(String), nullable=False)
    content_en = Column(String, nullable=False)
    content_kr = Column(String, nullable=False)
    publish_date = Column(DateTime, nullable=False)
    url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=False)
    title_en = Column(String, nullable=False)
    title_kr = Column(String, nullable=False)
    type = Column(Enum(NewsTypeEnum), nullable=False)

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
        :param publish_date: Date and time when the news was published
        :param url: URL of the news article
        :param source: Source of the news article
        :param source_id: Unique identifier from the source
        :param thumbnail_url: URL of the news thumbnail image
        :param title_en: Title of the news in English
        :param title_kr: Title of the news in Korean
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
