from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_competition_phase_response import (
    PulseliveFixtureDetailCompetitionPhaseResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_compseason_response import (
    PulseliveFixtureDetailCompSeasonResponse,
)


class PulseliveFixtureDetailGameweekResponse(CamelCaseModel):
    id: int
    comp_season: PulseliveFixtureDetailCompSeasonResponse
    gameweek: int
    competition_phase: PulseliveFixtureDetailCompetitionPhaseResponse
