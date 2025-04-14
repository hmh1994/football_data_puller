from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_table_entry_ground_location_response import (
    PulseliveStandingsTableEntryGroundLocationResponse,
)


class PulseliveStandingsTableEntryGroundResponse(CamelCaseModel):
    name: str
    city: str
    capacity: int | None = None
    location: PulseliveStandingsTableEntryGroundLocationResponse | None = None
    source: str
    id: int

    @field_validator("id", "capacity", mode="before")
    def convert_id_capacity(cls, value: Any) -> int:
        return convert_float_to_int(value)
