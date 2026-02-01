from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_competition_detail_season_response import (
    PulseliveNewCompetitionDetailSeasonResponse,
)


class PulseliveNewV1CompetitionDetailResponse(CamelCaseModel):
    """
    Response model for PulseLive v1 competition details API endpoint.

    Contains comprehensive competition information including all available seasons,
    competition metadata, and identification information. Used for pulling
    season data for a specific competition from the details endpoint.

    :ivar seasons: List of all available seasons for the competition
    :ivar code: Competition code (e.g., "EN_PR" for Premier League)
    :ivar name: Full competition name (e.g., "Premier League")
    :ivar id: Unique competition identifier
    """

    seasons: list[PulseliveNewCompetitionDetailSeasonResponse]
    code: str
    name: str
    id: str
