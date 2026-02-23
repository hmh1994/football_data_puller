from datetime import datetime
from typing import NotRequired, TypedDict

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
    short_name: NotRequired[str]


class PlayerIdDict(TypedDict, total=False):
    """Player ID info."""

    competition_id: str | None
    season_id: str | None
    player_id: str


class PlayerResponse(RawResponseModel):
    """Base player response. Requires id parsing validator."""

    country: CountryDict | None = None
    current_team: PlayerTeamDict | None = None
    id: PlayerIdDict
    name: PersonDict
    position: str

    @field_validator("id", mode="before")
    def parse_id(cls, v) -> dict:
        if isinstance(v, str):
            return {"player_id": v}
        return v

    @field_validator("name", mode="before")
    def parse_name(cls, v) -> dict:
        if isinstance(v, str):
            parts = v.split(" ", 1)
            return {
                "first": parts[0],
                "last": parts[1] if len(parts) > 1 else "",
                "display": v,
            }
        return v


class PlayerDatesResponse(RawResponseModel):
    """Player dates. Requires birth date parsing validator."""

    birth: datetime | None = None
    joined_club: str | None = None

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
    country_of_birth: str | None = None
    shirt_num: int | None = None
    weight: int | None = None
    dates: PlayerDatesResponse
    preferred_foot: str | None = None
    height: int | None = None


# Type aliases
V1PlayerDetailsResponse = PlayerDetailResponse
"""GET v1/competitions/{comp_id}/seasons/{season_id}/players/{player_id}"""

V1PlayerResponse = RootModel[list[PlayerDetailResponse]]
"""GET v1/players/{player_id} (list format)"""
