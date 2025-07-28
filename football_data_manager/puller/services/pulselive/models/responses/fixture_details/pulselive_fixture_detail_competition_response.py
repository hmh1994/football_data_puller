from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveFixtureDetailCompetitionResponse(CamelCaseModel):
    abbreviation: str
    description: str
    level: str
    source: str
    id: int
    alt_ids: dict[str, str] = dict()
