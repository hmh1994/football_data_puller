from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.match_stats.pulselive_match_stat_item_response import (
    PulseliveMatchStatItemResponse,
)


class PulseliveMatchStatTeamPositionResponse(CamelCaseModel):
    m: list[PulseliveMatchStatItemResponse]
