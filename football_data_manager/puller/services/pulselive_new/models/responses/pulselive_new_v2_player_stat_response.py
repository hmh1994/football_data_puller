from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_player_response import (
    PulseliveNewPlayerResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_player_stats_response import (
    PulseliveNewPlayerStatsResponse,
)


class PulseliveNewV2PlayerStatsResponse(CamelCaseModel):
    player: PulseliveNewPlayerResponse
    stats: PulseliveNewPlayerStatsResponse
