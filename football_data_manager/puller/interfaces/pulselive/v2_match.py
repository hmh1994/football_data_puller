from datetime import datetime
from typing import TypedDict

from pydantic import field_validator

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import (
    MatchTeamDict,
    PersonDict,
)


# --- v2/matches/{id} ---


class SeasonInfoDict(TypedDict):
    """Season info within match response."""

    name: str
    id: str


class V2MatchResponse(RawResponseModel):
    """GET v2/matches/{match_id}"""

    kickoffTimezone: str
    competitionId: str
    period: str
    matchWeek: int
    kickoff: datetime
    awayTeam: MatchTeamDict
    seasonInfo: SeasonInfoDict
    competition: str
    clock: str | None = None
    kickoffTimezoneString: str
    seasonId: str
    homeTeam: MatchTeamDict
    ground: str
    resultType: str | None = None
    matchId: str
    attendance: int | None = None

    @field_validator("kickoff", mode="before")
    def parse_custom_dt(cls, v) -> datetime:
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v


# --- v3/matches/{id}/lineups ---


class PlayerSimpleDict(TypedDict):
    """Simple player info used in lineups."""

    firstName: str | None
    lastName: str | None
    display: str | None
    shirtNum: str
    isCaptain: bool
    id: str
    position: str
    subPosition: str | None


class ManagerDict(TypedDict, total=False):
    """Manager info within lineup."""

    firstName: str | None
    lastName: str | None
    display: str | None
    id: str | None
    type: str | None


class FormationDict(TypedDict, total=False):
    """Formation info within lineup."""

    subs: list[str] | None
    teamId: str | None
    lineup: list[list[str]] | None
    formation: str | None


class TeamLineupDict(TypedDict):
    """Team lineup with players, formation, managers."""

    players: list[PlayerSimpleDict]
    formation: FormationDict
    managers: list[ManagerDict]


class V3MatchLineupResponse(RawResponseModel):
    """GET v3/matches/{match_id}/lineups"""

    awayTeam: TeamLineupDict
    homeTeam: TeamLineupDict
