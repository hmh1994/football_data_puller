from sqlalchemy import Column, String, ARRAY, DateTime

from football_data_manager.common.enums.news_type import NewsTypeEnum
from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.old_repositories.base_entity import BaseEntity
from football_data_manager.common.old_repositories.teams.team_entity import TeamEntity


class NewsEntity(BaseEntity):
    """
    News entity model.
    :ivar id: Unique identifier for the entity.
    :ivar team_ids: List of team IDs related to the news.
    :param author_en: List of authors in English.
    :param author_kr: List of authors in Korean.
    :param content_en: News content in English.
    :param content_kr: News content in Korean.
    :param publish_date: Date and time when the news was published.
    :param url: URL of the news article.
    :param source: Source of the news article.
    :param source_id: Unique identifier from the source.
    :param teams: List of teams related to the news.
    :param thumbnail_url: URL of the news thumbnail image.
    :param title_en: Title of the news in English.
    :param title_kr: Title of the news in Korean.
    :param type: Type of the news article.
    """

    __tablename__ = "news"

    author_en = Column(ARRAY(String), nullable=False)
    author_kr = Column(ARRAY(String), nullable=False)
    content_en = Column(String, nullable=False)
    content_kr = Column(String, nullable=False)
    publish_date = Column(DateTime, nullable=False)
    url = Column(String, nullable=False)
    source = Column(String, nullable=False)
    teams = Column(ARRAY(String), nullable=False)
    thumbnail_url = Column(String, nullable=False)
    title_en = Column(String, nullable=False)
    title_kr = Column(String, nullable=False)
    type = Column(String, nullable=False)

    def __init__(
        self,
        author_en: list[str],
        author_kr: list[str],
        content_en: str,
        content_kr: str,
        publish_date: DateTime,
        url: str,
        source: SourceEnum,
        source_id: str,
        teams: list[TeamEntity],
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
        self.source = source
        self.team_ids = [team.id for team in teams]
        self.teams = teams
        self.thumbnail_url = thumbnail_url
        self.title_en = title_en
        self.title_kr = title_kr
        self.type = typ.value.upper()
