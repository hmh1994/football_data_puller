from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)


class PulseliveCompseasonGameweekGameweekTimestampResponse(CamelCaseModel):
    completeness: int
    gmt_offset: int = 0
    label: str
    millis: int

    @field_validator("gmt_offset", mode="before")
    def convert_gmt_offset(cls, value: Any) -> int:
        return convert_float_to_int(value)
