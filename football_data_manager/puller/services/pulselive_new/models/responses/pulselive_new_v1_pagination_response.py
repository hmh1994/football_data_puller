from pydantic import Field

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewV1PaginationResponse(CamelCaseModel):
    """
    Response model for pagination information from PulseLive v1 API.

    Contains pagination metadata for paginated API responses including
    limits and cursor-based navigation tokens.

    :ivar limit: Maximum number of items per page
    :ivar prev: Previous page cursor token (null if on first page)
    :ivar next: Next page cursor token (null if on last page)
    """

    limit: int = Field(alias="_limit")
    prev: str | None = Field(alias="_prev")
    next: str | None = Field(alias="_next")