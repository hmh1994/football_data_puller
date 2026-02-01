from enum import StrEnum
from typing import Self


class PeriodEnum(StrEnum):
    """
    Enum for the period of football match.
    """

    FIRSTHALF = "firsthalf"
    FULLTIME = "fulltime"
    PREMATCH = "prematch"
    SECONDHALF = "secondhalf"
    UNKNOWN = "unknown"

    @classmethod
    def from_string(cls, source: str | None) -> Self:
        """
        Convert a string to a PeriodEnum member.
        """
        try:
            if source:
                return cls(source.lower())
            else:
                return cls.UNKNOWN
        except ValueError:
            return cls.UNKNOWN
