from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_comp_season_competition_response import (
    PulseliveTeamsCompseasonsStaffCompSeasonCompetitionResponse,
)


class PulseliveTeamsCompseasonsStaffCompSeasonResponse(CamelCaseModel):
    label: str
    competition: PulseliveTeamsCompseasonsStaffCompSeasonCompetitionResponse
    id: int

    @field_validator("id", mode="before")
    def convert_id(cls, value: Any) -> int:
        return convert_float_to_int(value)
