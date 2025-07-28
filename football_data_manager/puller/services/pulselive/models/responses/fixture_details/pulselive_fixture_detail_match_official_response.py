from typing import Any

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_name_response import (
    PulseliveFixtureDetailNameResponse,
)


class PulseliveFixtureDetailMatchOfficialResponse(CamelCaseModel):
    match_official_id: int
    role: str | None = None
    birth: dict[str, Any]
    name: PulseliveFixtureDetailNameResponse
    id: int
