from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_event_team_response import (
    PulseliveNewEventTeamResponse,
)


class PulseliveNewV1EventResponse(CamelCaseModel):
    away_team: PulseliveNewEventTeamResponse
    home_team: PulseliveNewEventTeamResponse
