from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveFixtureDetailCompetitionPhaseResponse(CamelCaseModel):
    id: int
    type: str
    gameweek_range: list[int]
