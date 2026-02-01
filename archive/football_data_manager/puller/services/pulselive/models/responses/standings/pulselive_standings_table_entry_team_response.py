from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_table_entry_team_club_response import (
    PulseliveStandingsTableEntryTeamClubResponse,
)


class PulseliveStandingsTableEntryTeamResponse(CamelCaseModel):
    name: str
    club: PulseliveStandingsTableEntryTeamClubResponse
    team_type: str
    short_name: str
    id: int
    alt_ids: dict[str, str]

    @field_validator("id", mode="before")
    def convert_id(cls, value: Any) -> int:
        return convert_float_to_int(value)
