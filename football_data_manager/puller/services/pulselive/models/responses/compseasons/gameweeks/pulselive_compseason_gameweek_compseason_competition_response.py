from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveCompseasonGameweekCompseasonCompetitionResponse(CamelCaseModel):
    abbreviation: str
    description: str
    id: int
    level: str
    source: str
