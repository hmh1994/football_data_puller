from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveCompseasonTeamGroundLocationResponse(CamelCaseModel):
    latitude: float
    longitude: float
