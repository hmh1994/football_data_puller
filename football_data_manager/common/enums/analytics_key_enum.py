from enum import StrEnum
from typing import Self


class AnalyticsKeyEnum(StrEnum):
    """
    Enum for analytics metric keys.

    Defines the types of analytics metrics that can be tracked and displayed.
    Values are stored in alphabetical order for consistency.

    :cvar PER_MATCH_GOALS: Average goals scored per match
    :cvar PER_MATCH_PASS_ACCURACY: Average pass accuracy percentage per match
    :cvar PER_MATCH_SUBSTITUTIONS: Average substitutions made per match
    :cvar PER_MATCH_XG: Expected goals (xG) per match
    :cvar PER_MATCH_YELLOW_CARDS: Average yellow cards per match
    :cvar TOTAL_GOALS: Total number of goals scored
    :cvar TOTAL_RED_CARDS: Total number of red cards received
    """

    PER_MATCH_GOALS = "per_match_goals"
    PER_MATCH_PASS_ACCURACY = "per_match_pass_accuracy"
    PER_MATCH_SUBSTITUTIONS = "per_match_substitutions"
    PER_MATCH_XG = "per_match_xg"
    PER_MATCH_YELLOW_CARDS = "per_match_yellow_cards"
    TOTAL_GOALS = "total_goals"
    TOTAL_RED_CARDS = "total_red_cards"

    @classmethod
    def from_string(cls, value: str) -> Self:
        """
        Convert a string to an AnalyticsKeyEnum member.

        :param value: String value to convert
        :returns: Matching enum member
        :raises ValueError: If no matching enum member is found
        """
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(f"Unknown analytics key: {value}")