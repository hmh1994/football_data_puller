from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_club_response import (
    PulseliveFixtureDetailClubResponse,
)


class PulseliveFixtureDetailTeamInfoResponse(CamelCaseModel):
    name: str
    club: PulseliveFixtureDetailClubResponse
    team_type: str
    short_name: str
    id: int
    alt_ids: dict[str, str] = dict()
