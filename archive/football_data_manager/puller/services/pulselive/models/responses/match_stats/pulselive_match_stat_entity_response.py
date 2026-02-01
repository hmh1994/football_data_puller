from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_clock_response import (
    PulseliveFixtureDetailClockResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_gameweek_response import (
    PulseliveFixtureDetailGameweekResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_ground_response import (
    PulseliveFixtureDetailGroundResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_kickoff_response import (
    PulseliveFixtureDetailKickoffResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_teamscore_response import (
    PulseliveFixtureDetailTeamScoreResponse,
)


class PulseliveMatchStatEntityResponse(CamelCaseModel):
    gameweek: PulseliveFixtureDetailGameweekResponse
    kickoff: PulseliveFixtureDetailKickoffResponse
    provisional_kickoff: PulseliveFixtureDetailKickoffResponse
    teams: list[PulseliveFixtureDetailTeamScoreResponse]
    replay: bool
    ground: PulseliveFixtureDetailGroundResponse
    neutral_ground: bool
    status: str
    phase: str
    outcome: str
    attendance: int
    clock: PulseliveFixtureDetailClockResponse
    fixture_type: str
    extra_time: bool
    shootout: bool
    behind_closed_doors: bool
    id: int
