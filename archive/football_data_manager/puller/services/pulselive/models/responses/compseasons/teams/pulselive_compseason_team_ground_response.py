from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.compseasons.teams.pulselive_compseason_team_ground_location_response import (
    PulseliveCompseasonTeamGroundLocationResponse,
)


class PulseliveCompseasonTeamGroundResponse(CamelCaseModel):
    capacity: int | None = None
    city: str
    id: int
    location: PulseliveCompseasonTeamGroundLocationResponse | None = None
    name: str
    source: str = ""

    @field_validator("id", "capacity", mode="before")
    def convert_id_and_capacity(cls, value: Any) -> int:
        return convert_float_to_int(value)
