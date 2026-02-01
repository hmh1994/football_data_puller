from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveFixtureDetailScoreResponse(CamelCaseModel):
    home_score: int
    away_score: int
