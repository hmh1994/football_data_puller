from typing import TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import (
    CountryDict,
    PersonDict,
)


class AwardTeamDict(TypedDict):
    """Team info within award."""

    id: str
    name: str
    shortName: str
    loan: int | None


class AwardDatesDict(TypedDict):
    """Date info within award."""

    birth: str
    joinedClub: str


class AwardCareerDict(TypedDict):
    """Career info within award."""

    seasonsInPremierLeague: list[str]
    firstPremierLeagueFixtureId: str
    seasonsAtCurrentTeam: list[str]


class PlayerAwardDict(TypedDict):
    """Player award entry."""

    id: str
    currentTeam: AwardTeamDict
    date: str
    country: CountryDict
    name: PersonDict
    dates: AwardDatesDict
    type: str
    shirtNum: int
    weight: int
    countryOfBirth: str
    position: str
    preferredFoot: str
    height: int


class ManagerAwardDict(TypedDict):
    """Manager award entry."""

    id: str
    currentTeam: AwardTeamDict
    date: str
    country: CountryDict
    name: PersonDict
    dates: AwardDatesDict
    type: str
    career: AwardCareerDict
    role: str


class V1AwardResponse(RawResponseModel):
    """GET v1/competitions/{comp_id}/seasons/{season_id}/awards"""

    managerAwards: list[ManagerAwardDict]
    playerAwards: list[PlayerAwardDict]
