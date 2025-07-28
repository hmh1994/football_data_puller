from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveFixtureDetailGroundResponse(CamelCaseModel):
    name: str
    city: str
    source: str
    id: int
