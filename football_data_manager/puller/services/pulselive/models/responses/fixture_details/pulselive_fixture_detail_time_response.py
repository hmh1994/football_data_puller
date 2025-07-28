from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveFixtureDetailTimeResponse(CamelCaseModel):
    millis: int
    label: str
    gmt_offset: int
