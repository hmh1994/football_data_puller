from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveFixtureDetailNameResponse(CamelCaseModel):
    display: str
    first: str
    last: str
