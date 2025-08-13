from enum import StrEnum
from typing import Self


class PositionEnum(StrEnum):
    """
    Enum for football positions.
    """

    GOALKEEPER = "goalkeeper"
    DEFENDER = "defender"
    FORWARD = "forward"
    MIDFIELDER = "midfielder"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, source: str) -> Self:
        """
        Convert a string to a PositionEnum member.
        """
        try:
            return cls(source.lower())
        except ValueError:
            return cls.UNKNOWN
