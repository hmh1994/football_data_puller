from enum import StrEnum
from typing import Self


class SideEnum(StrEnum):
    """
    Enum for sides in football.
    """

    RIGHT = "right"
    LEFT = "left"
    BOTH = "both"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, source: str | None) -> Self:
        """
        Convert a string to a SideEnum member.
        """
        try:
            if source:
                return cls(source.lower())
            else:
                return cls.UNKNOWN
        except ValueError:
            return cls.UNKNOWN
