from datetime import datetime
from typing import TypedDict

from pydantic import RootModel, field_validator

from football_data_manager.common.utils.type_helper.datetime_helper import (
    parse_date_string_to_utc,
)
from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import (
    CountryDict,
    PersonDict,
)


class PlayerTeamDict(TypedDict):
    """Team info within player response."""

    name: str
    id: str
    shortName: str | None


class PlayerIdDict(TypedDict, total=False):
    """Player ID info."""

    competitionId: str | None
    seasonId: str | None
    playerId: str


class PlayerResponse(RawResponseModel):
    """Base player response. Requires id parsing validator."""

    country: CountryDict
    currentTeam: PlayerTeamDict | None = None
    id: PlayerIdDict
    name: PersonDict
    position: str

    @field_validator("id", mode="before")
    def parse_id(cls, v) -> dict:
        if isinstance(v, str):
            return {"playerId": v}
        return v


class PlayerDatesResponse(RawResponseModel):
    """Player dates. Requires birth date parsing validator."""

    birth: datetime | None = None
    joinedClub: str | None = None

    @field_validator("birth", mode="before")
    def parse_birth_date(cls, v) -> datetime | None:
        if isinstance(v, str):
            try:
                return parse_date_string_to_utc(v)
            except ValueError:
                return None
        return v


class PlayerDetailResponse(PlayerResponse):
    """Detailed player information."""

    loan: int | None = None
    countryOfBirth: str | None = None
    shirtNum: int | None = None
    weight: int | None = None
    dates: PlayerDatesResponse
    preferredFoot: str | None = None
    height: int | None = None


# Type aliases
V1PlayerDetailsResponse = PlayerDetailResponse
"""GET v1/competitions/{comp_id}/seasons/{season_id}/players/{player_id}"""

V1PlayerResponse = RootModel[list[PlayerDetailResponse]]
"""GET v1/players/{player_id} (list format)"""
