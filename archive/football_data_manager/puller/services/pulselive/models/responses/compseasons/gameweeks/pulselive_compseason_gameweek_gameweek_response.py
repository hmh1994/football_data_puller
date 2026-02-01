from pydantic import Field

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.compseasons.gameweeks.pulselive_compseason_gameweek_gameweek_timestamp_response import (
    PulseliveCompseasonGameweekGameweekTimestampResponse,
)


class PulseliveCompseasonGameweekGameweekResponse(CamelCaseModel):
    gameweek: int
    from_: PulseliveCompseasonGameweekGameweekTimestampResponse = Field(alias="from")
    id: int
    matches: int
    status: str
    until: PulseliveCompseasonGameweekGameweekTimestampResponse
