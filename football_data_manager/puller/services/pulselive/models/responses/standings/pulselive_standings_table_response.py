from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_table_entry_response import (
    PulseliveStandingsTableEntryResponse,
)


class PulseliveStandingsTableResponse(CamelCaseModel):
    game_week: int
    entries: list[PulseliveStandingsTableEntryResponse]

    @field_validator("game_week", mode="before")
    def convert_gameweek(cls, value: Any) -> int:
        return convert_float_to_int(value)
