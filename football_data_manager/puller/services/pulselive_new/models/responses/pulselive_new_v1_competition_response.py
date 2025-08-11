from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_competition_item_response import (
    PulseliveNewCompetitionItemResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_pagination_response import (
    PulseliveNewV1PaginationResponse,
)


class PulseliveNewV1CompetitionResponse(CamelCaseModel):
    """
    Response model for PulseLive v1 competitions API endpoint.

    Represents the complete response from the competitions API including
    pagination information and the list of competition data.
    Maps to the response from https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v1/competitions

    :ivar pagination: Pagination metadata for the response
    :ivar data: List of competition items in the current page
    """

    pagination: PulseliveNewV1PaginationResponse
    data: list[PulseliveNewCompetitionItemResponse]