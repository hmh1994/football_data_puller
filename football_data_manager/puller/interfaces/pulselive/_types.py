from typing import NotRequired, TypedDict


class PersonDict(TypedDict):
    """Person name. Shared across multiple endpoints."""

    first: str
    last: str
    display: NotRequired[str]


class CountryDict(TypedDict):
    """Country info."""

    country: str
    iso_code: str | None
    demonym: str | None


class StadiumDict(TypedDict, total=False):
    """Stadium info (all fields optional)."""

    country: str | None
    city: str | None
    name: str | None
    capacity: int | None


class MatchTeamDict(TypedDict):
    """Team score info. Shared across fixture/match endpoints."""

    name: str
    id: str
    short_name: NotRequired[str]
    score: NotRequired[int]
    half_time_score: NotRequired[int]
    red_cards: NotRequired[int]


class PaginatedDict(TypedDict):
    """Pagination metadata."""

    _limit: int
    _prev: str | None
    _next: str | None
