from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_birth_response import (
    PulseliveTeamsCompseasonsStaffBirthResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_name_response import (
    PulseliveTeamsCompseasonsStaffNameResponse,
)


class PulseliveTeamsCompseasonsStaffOfficialResponse(CamelCaseModel):
    official_id: int
    role: str
    active: bool
    birth: PulseliveTeamsCompseasonsStaffBirthResponse
    age: str
    name: PulseliveTeamsCompseasonsStaffNameResponse
    id: int
    alt_ids: dict[str, str]

    @field_validator("official_id", "id", mode="before")
    def convert_official_id_id_appearances(cls, value: Any) -> int:
        return convert_float_to_int(value)
