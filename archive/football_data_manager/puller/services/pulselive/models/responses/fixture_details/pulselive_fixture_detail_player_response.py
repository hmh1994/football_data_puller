from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_birth_response import (
    PulseliveFixtureDetailBirthResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_country_response import (
    PulseliveFixtureDetailCountryResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_name_response import (
    PulseliveFixtureDetailNameResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_player_info_response import (
    PulseliveFixtureDetailPlayerInfoResponse,
)


class PulseliveFixtureDetailPlayerResponse(CamelCaseModel):
    match_position: str
    match_shirt_number: int
    captain: bool
    player_id: int
    info: PulseliveFixtureDetailPlayerInfoResponse
    national_team: PulseliveFixtureDetailCountryResponse
    birth: PulseliveFixtureDetailBirthResponse
    age: str
    name: PulseliveFixtureDetailNameResponse
    id: int
    alt_ids: dict[str, str] = dict()
