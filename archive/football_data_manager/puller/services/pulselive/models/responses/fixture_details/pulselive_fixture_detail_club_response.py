from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveFixtureDetailClubResponse(CamelCaseModel):
    name: str
    short_name: str
    abbr: str
    id: int
