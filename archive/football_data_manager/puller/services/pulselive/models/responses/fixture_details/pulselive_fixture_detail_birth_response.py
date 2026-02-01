from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_birth_date_response import (
    PulseliveFixtureDetailBirthDateResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_country_response import (
    PulseliveFixtureDetailCountryResponse,
)


class PulseliveFixtureDetailBirthResponse(CamelCaseModel):
    date: PulseliveFixtureDetailBirthDateResponse
    country: PulseliveFixtureDetailCountryResponse
    place: str | None = None
