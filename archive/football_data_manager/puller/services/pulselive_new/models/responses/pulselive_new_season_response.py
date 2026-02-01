from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewSeasonResponse(CamelCaseModel):
    name: str
    id: str
