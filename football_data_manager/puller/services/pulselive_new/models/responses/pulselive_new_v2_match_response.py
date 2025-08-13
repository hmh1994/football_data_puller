from datetime import datetime

from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_match_team_response import (
    PulseliveNewMatchTeamResponse,
)
from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_season_response import (
    PulseliveNewSeasonResponse,
)


class PulseliveNewV2MatchResponse(CamelCaseModel):
    kickoff_timezone: str
    competition_id: str
    period: str
    match_week: int
    kickoff: datetime
    away_team: PulseliveNewMatchTeamResponse
    season_info: PulseliveNewSeasonResponse
    competition: str
    clock: str
    kickoff_timezone_string: str
    season_id: str
    home_team: PulseliveNewMatchTeamResponse
    ground: str
    result_type: str
    match_id: str
    attendance: int

    @field_validator("kickoff", mode="before")
    def parse_custom_dt(cls, v) -> datetime:
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v
