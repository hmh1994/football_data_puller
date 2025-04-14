from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)


class PulseliveStandingsTableEntryStatResponse(CamelCaseModel):
    played: int
    won: int
    drawn: int
    lost: int
    goals_for: int
    goals_against: int
    goals_difference: int
    points: int

    @field_validator(
        "played",
        "won",
        "drawn",
        "lost",
        "goals_for",
        "goals_against",
        "goals_difference",
        "points",
        mode="before",
    )
    def convert_stat(cls, value: Any) -> int:
        return convert_float_to_int(value)
