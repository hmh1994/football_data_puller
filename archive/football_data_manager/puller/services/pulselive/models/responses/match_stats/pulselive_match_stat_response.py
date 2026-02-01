from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.match_stats.pulselive_match_stat_entity_response import (
    PulseliveMatchStatEntityResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.match_stats.pulselive_match_stat_team_position_response import (
    PulseliveMatchStatTeamPositionResponse,
)


class PulseliveMatchStatResponse(CamelCaseModel):
    entity: PulseliveMatchStatEntityResponse
    data: dict[str, PulseliveMatchStatTeamPositionResponse]
