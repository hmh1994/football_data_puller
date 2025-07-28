from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_match_stat_info_response import (
    PulseliveNewMatchStatInfoResponse,
)


class PulseliveNewV1MatchTeamStatResponse(CamelCaseModel):
    side: str
    stats: PulseliveNewMatchStatInfoResponse
    team_id: str
