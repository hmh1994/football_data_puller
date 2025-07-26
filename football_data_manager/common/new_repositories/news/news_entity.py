from datetime import datetime

from sqlalchemy import Column, String, ARRAY, DateTime
from sqlalchemy.ext.associationproxy import association_proxy

from football_data_manager.common.enums.news_type import NewsTypeEnum
from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.new_repositories.base_entity import BaseEntity
from football_data_manager.common.new_repositories.constants import NEWS_TABLE_NAME
from football_data_manager.common.new_repositories.news.news_team_association import (
    NewsTeamAssociation,
)


class NewsEntity(BaseEntity):
    """
    Entity model for news articles.
    :ivar id: Unique identifier for the entity.
    :ivar teams: List of teams related to the news.
    :param author_en: List of authors in English.
    :param author_kr: List of authors in Korean.
    :param content_en: News content in English.
    :param content_kr: News content in Korean.
    :param publish_date: Date and time when the news was published.
    :param url: URL of the news article.
    :param source: Source of the news article.
    :param source_id: Unique identifier from the source.
    :param thumbnail_url: URL of the news thumbnail image.
    :param title_en: Title of the news in English.
    :param title_kr: Title of the news in Korean.
    :param typ: Type of the news article.
    """

    __tablename__ = NEWS_TABLE_NAME

    author_en = Column(ARRAY(String), nullable=False)
    author_kr = Column(ARRAY(String), nullable=False)
    content_en = Column(String, nullable=False)
    content_kr = Column(String, nullable=False)
    publish_date = Column(DateTime, nullable=False)
    url = Column(String, nullable=False)
    source = Column(String, nullable=False)
    teams = association_proxy(
        target_collection=NewsTeamAssociation.TEAM_COLLECTION_NAME,
        attr=NewsTeamAssociation.TEAM_ATTRIBUTE_NAME,
        creator=lambda team: NewsTeamAssociation(team=team),  # type: ignore[arg-type]
    )
    thumbnail_url = Column(String, nullable=False)
    title_en = Column(String, nullable=False)
    title_kr = Column(String, nullable=False)
    type = Column(String, nullable=False)  # TODO: Change to Enum type

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
        super().__init__(source=source, source_id=source_id)
        self.author_en = author_en
        self.author_kr = author_kr
        self.content_en = content_en
        self.content_kr = content_kr
        self.publish_date = publish_date
        self.url = url
        self.thumbnail_url = thumbnail_url
        self.title_en = title_en
        self.title_kr = title_kr
        self.type = typ.value.upper()
