from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewFormationResponse(CamelCaseModel):
    subs: list[str]
    team_id: str
    lineup: list[list[str]]
    formation: str
