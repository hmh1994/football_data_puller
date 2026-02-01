from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_match_lineup_team_response import (
    PulseliveNewTeamLineupResponse,
)


class PulseliveNewV3MatchLineupResponse(CamelCaseModel):
    away_team: PulseliveNewTeamLineupResponse
    home_team: PulseliveNewTeamLineupResponse
