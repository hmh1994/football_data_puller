from enum import StrEnum
from typing import Self


class CardTypeEnum(StrEnum):
    FIRST_YELLOW = "yellow"
    SECOND_YELLOW = "secondyellow"
    DIRECT_RED = "straightred"

    @classmethod
    def from_string(cls, source: str) -> Self:
        """
        Convert a string to a CardTypeEnum member.
        """
        return cls(source.lower())
