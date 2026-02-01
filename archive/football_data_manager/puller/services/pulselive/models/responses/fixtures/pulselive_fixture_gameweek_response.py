from typing import Any

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.pydantic_helper.field_validators import (
    convert_float_to_int,
)
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_gameweek_comp_season_response import (
    PulseliveFixtureGameweekCompSeasonResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_gameweek_competition_phase_response import (
    PulseliveFixtureGameweekCompetitionPhaseResponse,
)


class PulseliveFixtureGameweekResponse(CamelCaseModel):
    id: int
    comp_season: PulseliveFixtureGameweekCompSeasonResponse
    gameweek: int
    competitionPhase: PulseliveFixtureGameweekCompetitionPhaseResponse

    @field_validator("id", "gameweek", mode="before")
    def convert_id_gameweek(cls, value: Any) -> int:
        return convert_float_to_int(value)
