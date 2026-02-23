from typing import NotRequired, TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel


class ArticleAuthorDict(TypedDict):
    """Article author information."""

    name: str
    url: str
    sameAs: NotRequired[str | list[str]]


class ArticleResponse(RawResponseModel):
    """Article response."""

    author: list[ArticleAuthorDict]
    dateCreated: str
    datePublished: str
    dateModified: str
    articleBody: str | None = None
    description: str
    headline: str
    thumbnailUrl: str


class NewsTranslateObjectDict(TypedDict):
    """Translation object with en/ko pair."""

    en: str
    ko: str


class NewsTranslateSummaryDict(TypedDict):
    """Translation summary with en/ko lists."""

    en: list[str]
    ko: list[str]


class NewsTranslateResponse(RawResponseModel):
    """News translation response."""

    article: int
    authors: list[NewsTranslateObjectDict]
    title: NewsTranslateObjectDict
    summary: NewsTranslateSummaryDict
    teams: list[str]
