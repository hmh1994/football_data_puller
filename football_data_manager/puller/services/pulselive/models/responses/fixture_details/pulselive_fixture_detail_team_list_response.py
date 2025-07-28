from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_formation_response import (
    PulseliveFixtureDetailFormationResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_player_response import (
    PulseliveFixtureDetailPlayerResponse,
)


class PulseliveFixtureDetailTeamListResponse(CamelCaseModel):
    team_id: int
    lineup: list[PulseliveFixtureDetailPlayerResponse]
    substitutes: list[PulseliveFixtureDetailPlayerResponse]
    formation: PulseliveFixtureDetailFormationResponse
