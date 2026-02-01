from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_birth_response import (
    PulseliveTeamsCompseasonsStaffBirthResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_country_response import (
    PulseliveTeamsCompseasonsStaffCountryResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_date_response import (
    PulseliveTeamsCompseasonsStaffDateResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_name_response import (
    PulseliveTeamsCompseasonsStaffNameResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_player_award_response import (
    PulseliveTeamsCompseasonsStaffPlayerAwardResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_player_info_response import (
    PulseliveTeamsCompseasonsStaffPlayerInfoResponse,
)


class PulseliveTeamsCompseasonsStaffPlayerResponse(CamelCaseModel):
    player_id: int
    info: PulseliveTeamsCompseasonsStaffPlayerInfoResponse
    national_team: PulseliveTeamsCompseasonsStaffCountryResponse
    height: int | None = None
    weight: int | None = None
    latest_position: str
    appearances: int
    goals: int | None = None
    assists: int | None = None
    tackles: int | None = None
    shots: int | None = None
    key_passes: int | None = None
    clean_sheets: int | None = None
    saves: int | None = None
    goals_conceded: int | None = None
    awards: dict[str, list[PulseliveTeamsCompseasonsStaffPlayerAwardResponse]] = dict()
    join_date: PulseliveTeamsCompseasonsStaffDateResponse
    leave_date: PulseliveTeamsCompseasonsStaffDateResponse | None = None
    birth: PulseliveTeamsCompseasonsStaffBirthResponse
    age: str | None = None
    name: PulseliveTeamsCompseasonsStaffNameResponse
    id: int
    alt_ids: dict[str, str]

    @field_validator("player_id", "id", "appearances", mode="before")
    def convert_player_id_id_appearances(cls, value: Any) -> int:
        return convert_float_to_int(value)

    @field_validator(
        "goals",
        "assists",
        "tackles",
        "shots",
        "key_passes",
        "clean_sheets",
        "saves",
        "goals_conceded",
        mode="before",
    )
    def convert_data(cls, value: Any) -> int | None:
        return convert_float_to_int(value) if value is not None else None
