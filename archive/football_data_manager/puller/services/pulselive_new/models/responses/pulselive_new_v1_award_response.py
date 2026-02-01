from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_manager_award_response import (
    PulseliveNewManagerAwardResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_player_award_response import (
    PulseliveNewPlayerAwardResponse,
)


class PulseliveNewV1AwardResponse(CamelCaseModel):
    """
    Response from PulseLive v1 awards API endpoint.

    Contains lists of manager awards and player awards for a specific
    competition season. Awards include various types such as Manager/Player
    of the Month, Goal of the Month, and Save of the Month.

    :ivar manager_awards: List of manager awards
    :ivar player_awards: List of player awards
    """

    manager_awards: list[PulseliveNewManagerAwardResponse]
    player_awards: list[PulseliveNewPlayerAwardResponse]
