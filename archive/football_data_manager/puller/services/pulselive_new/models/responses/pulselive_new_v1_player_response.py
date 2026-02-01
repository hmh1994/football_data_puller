from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_list_response import (
    PulseliveNewListResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_player_detail_response import (
    PulseliveNewPlayerDetailResponse,
)

# PulseLive v1 players API response as a list of player responses
PulseliveNewV1PlayerResponse = PulseliveNewListResponse[
    PulseliveNewPlayerDetailResponse
]
