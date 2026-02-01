from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewCompetitionItemResponse(CamelCaseModel):
    """
    Response model for individual competition item from PulseLive v1 competitions API.

    Represents a single competition entry with basic identification information.
    Used as part of the competitions list response.

    :ivar code: Competition code identifier (e.g., 'EN_FA', 'EN_D1')
    :ivar name: Full competition name (e.g., 'English FA Cup')
    :ivar id: Unique competition identifier as string
    """

    code: str
    name: str
    id: str