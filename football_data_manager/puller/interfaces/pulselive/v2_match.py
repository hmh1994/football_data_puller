from datetime import datetime
from typing import NotRequired, TypedDict

from pydantic import field_validator

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import (
    MatchTeamDict,
)


# --- v2/matches/{id} ---


class SeasonInfoDict(TypedDict):
    """Season info within match response."""

    name: str
    id: str


class V2MatchResponse(RawResponseModel):
    """GET v2/matches/{match_id}"""

    kickoff_timezone: str
    competition_id: str
    period: str
    match_week: int
    kickoff: datetime
    away_team: MatchTeamDict
    season_info: SeasonInfoDict
    competition: str
    clock: str | None = None
    kickoff_timezone_string: str
    season_id: str
    home_team: MatchTeamDict
    ground: str
    result_type: str | None = None
    match_id: str
    attendance: int | None = None

    @field_validator("kickoff", mode="before")
    def parse_custom_dt(cls, v) -> datetime:
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v


# --- v3/matches/{id}/lineups ---


class PlayerSimpleDict(TypedDict):
    """Simple player info used in lineups."""

    first_name: NotRequired[str]
    last_name: NotRequired[str]
    display: NotRequired[str]
    shirt_num: str
    is_captain: bool
    id: str
    position: str
    sub_position: NotRequired[str]


class ManagerDict(TypedDict, total=False):
    """Manager info within lineup."""

    first_name: str | None
    last_name: str | None
    display: str | None
    id: str | None
    type: str | None


class FormationDict(TypedDict, total=False):
    """Formation info within lineup."""

    subs: list[str] | None
    team_id: str | None
    lineup: list[list[str]] | None
    formation: str | None


class TeamLineupDict(TypedDict):
    """Team lineup with players, formation, managers."""

    players: list[PlayerSimpleDict]
    formation: FormationDict
    managers: list[ManagerDict]


class V3MatchLineupResponse(RawResponseModel):
    """GET v3/matches/{match_id}/lineups"""

    away_team: TeamLineupDict
    home_team: TeamLineupDict
