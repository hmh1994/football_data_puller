from typing import NotRequired, TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import (
    CountryDict,
    PersonDict,
)


class AwardTeamDict(TypedDict):
    """Team info within award."""

    id: str
    name: str
    short_name: str
    loan: NotRequired[int]


class AwardDatesDict(TypedDict):
    """Date info within award."""

    birth: str
    joined_club: str


class AwardCareerDict(TypedDict):
    """Career info within award."""

    seasons_in_premier_league: list[str]
    first_premier_league_fixture_id: NotRequired[str]
    seasons_at_current_team: list[str]


class PlayerAwardDict(TypedDict):
    """Player award entry."""

    id: str
    current_team: AwardTeamDict
    date: str
    country: CountryDict
    name: PersonDict
    dates: AwardDatesDict
    type: str
    shirt_num: int
    weight: int
    country_of_birth: str
    position: str
    preferred_foot: str
    height: int


class ManagerAwardDict(TypedDict):
    """Manager award entry."""

    id: str
    current_team: AwardTeamDict
    date: str
    country: CountryDict
    name: PersonDict
    dates: AwardDatesDict
    type: str
    career: AwardCareerDict
    role: str


class V1AwardResponse(RawResponseModel):
    """GET v1/competitions/{comp_id}/seasons/{season_id}/awards"""

    manager_awards: list[ManagerAwardDict]
    player_awards: list[PlayerAwardDict]
