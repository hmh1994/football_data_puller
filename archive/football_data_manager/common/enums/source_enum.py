from enum import StrEnum
from typing import Self


class SourceEnum(StrEnum):
    """
    Enum for data sources.
    """

    PULSELIVE = "pulselive"
    THE_ATHLETIC = "the_athletic"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, source: str) -> Self:
        """
        Convert a string to a SourceEnum member.
        """
        try:
            return cls(source.lower())
        except ValueError:
            return cls.UNKNOWN
