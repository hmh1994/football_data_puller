from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)


class PulseliveTeamsCompseasonsStaffPlayerInfoResponse(CamelCaseModel):
    position: str
    shirt_num: int | None = None
    position_info: str

    @field_validator("shirt_num", mode="before")
    def convert_shirt_num(cls, value: Any) -> int:
        return convert_float_to_int(value)
