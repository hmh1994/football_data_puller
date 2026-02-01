from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_player_detail_response import (
    PulseliveNewPlayerDetailResponse,
)


class PulseliveNewV2SquadResponse(CamelCaseModel):
    """
    Response from PulseLive v2 squad API endpoint.

    Contains list of players for a specific team in a competition season
    from the squad API endpoint.

    :ivar players: List of players in the squad
    """

    players: list[PulseliveNewPlayerDetailResponse]
