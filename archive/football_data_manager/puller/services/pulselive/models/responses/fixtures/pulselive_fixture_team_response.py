from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_team_detail_response import (
    PulseliveFixtureTeamDetailResponse,
)


class PulseliveFixtureTeamResponse(CamelCaseModel):
    team: PulseliveFixtureTeamDetailResponse
    score: int | None = None

    @field_validator("score", mode="before")
    def convert_score(cls, value: Any) -> int:
        return convert_float_to_int(value)
