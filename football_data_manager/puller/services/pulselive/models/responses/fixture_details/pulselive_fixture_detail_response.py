from typing import Any

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_clock_response import (
    PulseliveFixtureDetailClockResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_event_response import (
    PulseliveFixtureDetailEventResponse,
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
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_match_official_response import (
    PulseliveFixtureDetailMatchOfficialResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_score_response import (
    PulseliveFixtureDetailScoreResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_team_list_response import (
    PulseliveFixtureDetailTeamListResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_teamscore_response import (
    PulseliveFixtureDetailTeamScoreResponse,
)


class PulseliveFixtureDetailResponse(CamelCaseModel):
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
    match_officials: list[PulseliveFixtureDetailMatchOfficialResponse]
    half_time_score: PulseliveFixtureDetailScoreResponse
    team_lists: list[PulseliveFixtureDetailTeamListResponse]
    events: list[PulseliveFixtureDetailEventResponse]
    penalty_shootouts: list[Any]
    behind_closed_doors: bool
    id: int
    alt_ids: dict[str, str]
    metadata: dict[str, Any]
    source: str
