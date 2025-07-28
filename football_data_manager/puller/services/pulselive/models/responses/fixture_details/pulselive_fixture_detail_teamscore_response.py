from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_teaminfo_response import (
    PulseliveFixtureDetailTeamInfoResponse,
)


class PulseliveFixtureDetailTeamScoreResponse(CamelCaseModel):
    team: PulseliveFixtureDetailTeamInfoResponse
    score: int
