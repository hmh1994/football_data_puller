from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewFormationResponse(CamelCaseModel):
    subs: list[str] | None = None
    team_id: str | None = None
    lineup: list[list[str]] | None = None
    formation: str | None = None
