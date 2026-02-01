from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveTeamsCompseasonsStaffNameResponse(CamelCaseModel):
    display: str
    first: str
    middle: str | None = None
    last: str
