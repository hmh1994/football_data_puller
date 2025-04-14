from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_comp_season_competition_response import (
    PulseliveStandingsCompSeasonCompetitionResponse,
)


class PulseliveStandingsCompSeasonResponse(CamelCaseModel):
    label: str
    competition: PulseliveStandingsCompSeasonCompetitionResponse
    id: int

    @field_validator("id", mode="before")
    def convert_id(cls, value: Any) -> int:
        return convert_float_to_int(value)
