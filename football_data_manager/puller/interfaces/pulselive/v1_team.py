from typing import NotRequired, TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import (
    PaginatedDict,
    StadiumDict,
)


class TeamItemDict(TypedDict):
    """Team item with stadium data."""

    id: str
    name: str
    short_name: NotRequired[str]
    abbr: str
    stadium: StadiumDict


class V1TeamsResponse(RawResponseModel):
    """GET v1/competitions/{comp_id}/seasons/{season_id}/teams"""

    pagination: PaginatedDict
    data: list[TeamItemDict]
