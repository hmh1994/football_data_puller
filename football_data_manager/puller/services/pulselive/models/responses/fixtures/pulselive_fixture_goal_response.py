from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_clock_response import (
    PulseliveFixtureClockResponse,
)


class PulseliveFixtureGoalResponse(CamelCaseModel):
    person_id: int
    assist_id: int | None = None
    clock: PulseliveFixtureClockResponse
    phase: str
    type: str
    description: str

    @field_validator("person_id", "assist_id", mode="before")
    def convert_person_id_assist_id(cls, value: Any) -> int:
        return convert_float_to_int(value)
