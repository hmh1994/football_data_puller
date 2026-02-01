from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_manager_response import (
    PulseliveNewManagerResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_match_lineup_formation_response import (
    PulseliveNewFormationResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_player_simple_response import (
    PulseliveNewPlayerSimpleResponse,
)


class PulseliveNewTeamLineupResponse(CamelCaseModel):
    players: list[PulseliveNewPlayerSimpleResponse]
    formation: PulseliveNewFormationResponse
    managers: list[PulseliveNewManagerResponse]
