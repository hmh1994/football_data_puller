from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveFixtureDetailPlayerInfoResponse(CamelCaseModel):
    position: str
    shirt_num: int
    position_info: str
    loan: bool = False
