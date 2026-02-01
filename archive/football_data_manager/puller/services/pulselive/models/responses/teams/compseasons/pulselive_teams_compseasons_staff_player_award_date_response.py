from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)


class PulseliveTeamsCompseasonsStaffPlayerAwardDateResponse(CamelCaseModel):
    year: int
    month: int
    day: int

    @field_validator("year", "month", "day", mode="before")
    def convert_year_month_day(cls, value: Any) -> int:
        return convert_float_to_int(value)
