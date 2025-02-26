from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)


class PulseliveFixtureGameweekCompetitionPhaseResponse(CamelCaseModel):
    id: int
    type: str
    gameweek_range: tuple[int, int]

    @field_validator("id", mode="before")
    def convert_id(cls, value: Any) -> int:
        return convert_float_to_int(value)

    @field_validator("gameweek_range", mode="before")
    def convert_gameweek_range(cls, value: list[Any]) -> tuple[int]:
        return convert_float_to_int(value[0]), convert_float_to_int(value[1])
