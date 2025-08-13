from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_paginated_response import (
    PulseliveNewPaginatedResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_team_response import (
    PulseliveNewTeamResponse,
)


class PulseliveNewV1TeamsResponse(CamelCaseModel):
    """
    Response from PulseLive v1 teams API endpoint.

    Contains paginated list of teams for a specific competition season
    with their associated stadium information.
    """

    pagination: PulseliveNewPaginatedResponse
    data: list[PulseliveNewTeamResponse]
