from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewCompetitionDetailSeasonResponse(CamelCaseModel):
    """
    Response model for season information in competition details.

    Represents individual season data from the PulseLive v1 competition details API.
    Contains season name and unique identifier for further API operations.

    :ivar season: Full season name (e.g., "Season 2024/2025")
    :ivar id: Unique season identifier for API requests
    """

    season: str
    id: str
