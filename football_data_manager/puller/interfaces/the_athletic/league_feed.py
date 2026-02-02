from typing import TypedDict

from pydantic import BaseModel

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.the_athletic._types import AuthorDict


class LeagueFeedContentDict(TypedDict, total=False):
    """Individual content item within feed layout."""

    title: str | None
    consumable_id: str | None
    author: AuthorDict | None
    excerpt: str | None
    image_uri: str | None
    permalink: str | None


class LeagueFeedLayoutDict(TypedDict):
    """Layout within feed mulligan response."""

    type: str
    typename: str
    contents: list[LeagueFeedContentDict]


class LeagueFeedMulliganDict(TypedDict):
    """Feed mulligan response containing layouts."""

    layouts: list[LeagueFeedLayoutDict]


class LeagueFeedResponse(RawResponseModel):
    """LeagueFeedQuery GraphQL response."""

    feedMulligan: LeagueFeedMulliganDict


class QueryVariables(BaseModel):
    """GraphQL query variables (for requests, not responses)."""

    feed: str = "league"
    feed_id: int
    is_mobile_web: bool = False
    locale: str = "en-gb"
    show_long_titles: bool = False
    page: int = 0
    retrieveMeta: bool = False
