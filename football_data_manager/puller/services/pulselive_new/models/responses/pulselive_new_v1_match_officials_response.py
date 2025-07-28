from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_official_response import (
    PulseliveNewOfficialResponse,
)


class PulseliveNewV1MatchOfficialsResponse(CamelCaseModel):
    match_id: str
    match_officials: list[PulseliveNewOfficialResponse]
