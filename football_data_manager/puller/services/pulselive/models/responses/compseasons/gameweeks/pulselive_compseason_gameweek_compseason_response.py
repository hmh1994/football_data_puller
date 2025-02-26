from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.compseasons.gameweeks.pulselive_compseason_gameweek_compseason_competition_response import (
    PulseliveCompseasonGameweekCompseasonCompetitionResponse,
)


class PulseliveCompseasonGameweekCompseasonResponse(CamelCaseModel):
    competition: PulseliveCompseasonGameweekCompseasonCompetitionResponse
    id: int
    label: str
