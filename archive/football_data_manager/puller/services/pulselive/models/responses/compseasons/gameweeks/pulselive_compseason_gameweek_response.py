from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.compseasons.gameweeks.pulselive_compseason_gameweek_compseason_response import (
    PulseliveCompseasonGameweekCompseasonResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.compseasons.gameweeks.pulselive_compseason_gameweek_gameweek_response import (
    PulseliveCompseasonGameweekGameweekResponse,
)


class PulseliveCompSeasonGameweekResponse(CamelCaseModel):
    comp_season: PulseliveCompseasonGameweekCompseasonResponse
    gameweeks: list[PulseliveCompseasonGameweekGameweekResponse]
