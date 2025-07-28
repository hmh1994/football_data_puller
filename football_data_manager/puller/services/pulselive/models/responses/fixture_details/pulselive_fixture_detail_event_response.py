from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_clock_response import (
    PulseliveFixtureDetailClockResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_score_response import (
    PulseliveFixtureDetailScoreResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_time_response import (
    PulseliveFixtureDetailTimeResponse,
)


class PulseliveFixtureDetailEventResponse(CamelCaseModel):
    id: int | None = None
    person_id: int | None = None
    team_id: int | None = None
    assist_id: int | None = None
    clock: PulseliveFixtureDetailClockResponse
    phase: str
    type: str
    description: str | None = None
    time: PulseliveFixtureDetailTimeResponse
    score: PulseliveFixtureDetailScoreResponse
