from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_time_response import (
    PulseliveFixtureDetailTimeResponse,
)


class PulseliveFixtureDetailKickoffResponse(PulseliveFixtureDetailTimeResponse):
    completeness: int
