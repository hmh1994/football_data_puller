from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)


class PulseliveTeamsCompseasonsStaffDateResponse(CamelCaseModel):
    millis: int
    label: str

    @field_validator("millis", mode="before")
    def convert_millis(cls, value: Any) -> int:
        return convert_float_to_int(value)
