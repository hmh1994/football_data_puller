from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_competition_response import (
    PulseliveFixtureDetailCompetitionResponse,
)


class PulseliveFixtureDetailCompSeasonResponse(CamelCaseModel):
    label: str
    competition: PulseliveFixtureDetailCompetitionResponse
    id: int
