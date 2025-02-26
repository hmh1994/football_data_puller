from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)


class PulseliveFixtureKickoffResponse(CamelCaseModel):
    completeness: int
    millis: int | None = None
    label: str | None = None
    gmt_offset: int | None = None

    @field_validator("completeness", mode="before")
    def convert_completeness(cls, value: Any) -> int:
        return convert_float_to_int(value)

    @field_validator("millis", "gmt_offset", mode="before")
    def convert_millis_gmt_offset(cls, value: Any) -> int:
        return convert_float_to_int(value) if value is not None else None
