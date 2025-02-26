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
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_gameweek_response import (
    PulseliveFixtureGameweekResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_goal_response import (
    PulseliveFixtureGoalResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_ground_response import (
    PulseliveFixtureGroundResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_kickoff_response import (
    PulseliveFixtureKickoffResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_team_response import (
    PulseliveFixtureTeamResponse,
)


class PulseliveFixtureResponse(CamelCaseModel):
    gameweek: PulseliveFixtureGameweekResponse
    kickoff: PulseliveFixtureKickoffResponse
    provisional_kickoff: PulseliveFixtureKickoffResponse
    teams: tuple[PulseliveFixtureTeamResponse, PulseliveFixtureTeamResponse]
    replay: bool
    ground: PulseliveFixtureGroundResponse
    neutral_ground: bool
    status: str
    phase: str
    outcome: str | None = None
    attendance: int | None = None
    clock: PulseliveFixtureClockResponse | None = None
    fixture_type: str
    extra_time: bool
    shootout: bool
    goals: list[PulseliveFixtureGoalResponse]
    penalty_shootout: list[PulseliveFixtureGoalResponse] = list()
    behind_closed_doors: bool
    id: int
    alt_ids: dict[str, str]

    @field_validator("id", "attendance", mode="before")
    def convert_id_attendance(cls, value: Any) -> int:
        return convert_float_to_int(value)

    @field_validator("teams", mode="before")
    def convert_teams(
        cls, value: list[Any]
    ) -> tuple[PulseliveFixtureTeamResponse, PulseliveFixtureTeamResponse]:
        return PulseliveFixtureTeamResponse.model_validate(
            value[0]
        ), PulseliveFixtureTeamResponse.model_validate(value[1])
