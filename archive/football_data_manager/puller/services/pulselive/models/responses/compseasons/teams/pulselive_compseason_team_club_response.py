from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)


class PulseliveCompseasonTeamClubResponse(CamelCaseModel):
    abbr: str
    id: int
    name: str
    short_name: str

    @field_validator("id", mode="before")
    def convert_id(cls, value: Any) -> int:
        return convert_float_to_int(value)
