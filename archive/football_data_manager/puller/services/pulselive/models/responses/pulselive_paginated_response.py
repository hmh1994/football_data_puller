from typing import TypeVar, Generic

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.pulselive_page_info_response import (
    PulselivePageInfoResponse,
)

TResponse = TypeVar("TResponse", bound=CamelCaseModel)


class PulselivePaginatedResponse(CamelCaseModel, Generic[TResponse]):
    page_info: PulselivePageInfoResponse
    content: list[TResponse]
