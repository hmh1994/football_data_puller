from typing import TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import PaginatedDict


class CompetitionItemDict(TypedDict):
    """Individual competition item."""

    code: str
    name: str
    id: str


class V1CompetitionResponse(RawResponseModel):
    """GET v1/competitions"""

    pagination: PaginatedDict
    data: list[CompetitionItemDict]


class CompetitionDetailSeasonDict(TypedDict):
    """Season info within competition detail."""

    season: str
    id: str


class V1CompetitionDetailResponse(RawResponseModel):
    """GET v1/competitions/{id}/details"""

    seasons: list[CompetitionDetailSeasonDict]
    code: str
    name: str
    id: str
