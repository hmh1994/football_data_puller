from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewTeamResponse(CamelCaseModel):
    score: int
    name: str
    id: str
    half_time_score: int
    short_name: str
    abbr: str
    red_cards: int
