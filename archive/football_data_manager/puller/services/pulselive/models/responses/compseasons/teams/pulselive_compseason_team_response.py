from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.compseasons.teams.pulselive_compseason_team_club_response import (
    PulseliveCompseasonTeamClubResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.compseasons.teams.pulselive_compseason_team_ground_response import (
    PulseliveCompseasonTeamGroundResponse,
)


class PulseliveCompseasonTeamResponse(CamelCaseModel):
    club: PulseliveCompseasonTeamClubResponse
    grounds: list[PulseliveCompseasonTeamGroundResponse]
    id: int
    name: str
    short_name: str
    team_type: str
    alt_ids: dict[str, str]

    @field_validator("id", mode="before")
    def convert_id(cls, value: Any) -> int:
        return convert_float_to_int(value)
