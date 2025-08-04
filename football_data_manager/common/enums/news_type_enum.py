from enum import StrEnum
from typing import Self


class NewsTypeEnum(StrEnum):
    """
    Enum for types of news articles.
    """

    FULL_ARTICLE = "full_article"
    TWEET_SUMMARY = "tweet_summary"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, source: str) -> Self:
        """
        Convert a string to a NewsTypeEnum member.
        """
        try:
            return cls(source.lower())
        except ValueError:
            return cls.UNKNOWN
