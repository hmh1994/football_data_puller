from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_table_entry_annotation_response import (
    PulseliveStandingsTableEntryAnnotationResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_table_entry_ground_response import (
    PulseliveStandingsTableEntryGroundResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_table_entry_stat_response import (
    PulseliveStandingsTableEntryStatResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_table_entry_team_response import (
    PulseliveStandingsTableEntryTeamResponse,
)


class PulseliveStandingsTableEntryResponse(CamelCaseModel):
    team: PulseliveStandingsTableEntryTeamResponse
    position: int
    starting_position: int
    overall: PulseliveStandingsTableEntryStatResponse
    home: PulseliveStandingsTableEntryStatResponse
    away: PulseliveStandingsTableEntryStatResponse
    annotations: list[PulseliveStandingsTableEntryAnnotationResponse] = []
    # form: list[PulseliveFixtureResponse]
    ground: PulseliveStandingsTableEntryGroundResponse

    @field_validator("position", "starting_position", mode="before")
    def convert_position(cls, value: Any) -> int:
        return convert_float_to_int(value)
