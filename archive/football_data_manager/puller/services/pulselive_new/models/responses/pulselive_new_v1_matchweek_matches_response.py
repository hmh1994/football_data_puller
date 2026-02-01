from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_match_response import (
    PulseliveNewMatchResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_paginated_response import (
    PulseliveNewPaginatedResponse,
)


class PulseliveNewV1MatchweekMatchesResponse(CamelCaseModel):
    """
    Response model for PulseLive v1 matchweek matches API endpoint.

    Contains paginated list of matches for a specific competition season
    and matchweek, including pagination metadata for retrieving additional pages.

    :ivar pagination: Pagination information for the response
    :ivar data: List of matches in the current page
    """

    pagination: PulseliveNewPaginatedResponse
    data: list[PulseliveNewMatchResponse]
