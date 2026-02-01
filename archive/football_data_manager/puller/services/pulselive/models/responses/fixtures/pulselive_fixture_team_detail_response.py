from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_team_detail_club_response import (
    PulseliveFixtureTeamDetailClubResponse,
)


class PulseliveFixtureTeamDetailResponse(CamelCaseModel):
    name: str
    club: PulseliveFixtureTeamDetailClubResponse
    team_type: str
    short_name: str
    id: int
    alt_ids: dict[str, str]

    @field_validator("id", mode="before")
    def convert_id(cls, value: Any) -> int:
        return convert_float_to_int(value)
