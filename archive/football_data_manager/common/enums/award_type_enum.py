from enum import Enum
from typing import Self


class AwardTypeEnum(Enum):
    """
    Enum for award types in football competitions.

    Defines standardized award categories for player and staff achievements
    including monthly awards, seasonal awards, and special recognitions.
    """

    # Player Awards
    PLAYER_OF_THE_MONTH = "POTM"
    GOAL_OF_THE_MONTH = "GOTM"
    SAVE_OF_THE_MONTH = "SOTM"
    PLAYER_OF_THE_SEASON = "POTS"
    YOUNG_PLAYER_OF_THE_SEASON = "YPOTS"
    PLAYMAKER_OF_THE_SEASON = "PM"
    GOAL_OF_THE_SEASON = "GOTS"
    MOST_POWERFUL_GOAL_OF_THE_SEASON = "MPGOTS"
    SAVE_OF_THE_SEASON = "SOTS"
    GOLDEN_BOOT = "GB"
    GOLDEN_GLOVE = "GG"
    MOST_IMPROBABLE_COMEBACK_OF_THE_SEASON = "MICOTS"
    GAMECHANGER_OF_THE_SEASON = "GCOTS"

    # Manager Awards
    MANAGER_OF_THE_MONTH = "MOTM"
    MANAGER_OF_THE_SEASON = "MOTS"

    @classmethod
    def from_string(cls, award_type_str: str) -> Self:
        """
        Map award type string from API to AwardTypeEnum.

        Uses enum values to find matching award type, eliminating duplicate mappings.

        :param award_type_str: Award type string (e.g., "POTM", "GOTM", "SOTM", "MOTM", "MOTS")
        :returns: Corresponding AwardTypeEnum member
        :raises ValueError: If award type string is not recognized
        """
        for award_type in cls:
            if award_type.value == award_type_str:
                return award_type

        valid_values = [award.value for award in cls]
        raise ValueError(
            f"Unknown award type: {award_type_str}. "
            f"Expected one of: {', '.join(valid_values)}"
        )
