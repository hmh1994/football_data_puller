from typing import TypedDict


class PersonDict(TypedDict):
    """Person name. Shared across multiple endpoints."""

    simpleName: str
    fullName: str


class CountryDict(TypedDict):
    """Country info."""

    country: str
    isoCode: str | None
    demonym: str | None


class StadiumDict(TypedDict, total=False):
    """Stadium info (all fields optional)."""

    country: str | None
    city: str | None
    name: str | None
    capacity: int | None


class MatchTeamDict(TypedDict):
    """Team score info. Shared across fixture/match endpoints."""

    score: int | None
    name: str
    id: str
    halfTimeScore: int | None
    shortName: str | None
    redCards: int | None


class PaginatedDict(TypedDict):
    """Pagination metadata."""

    _limit: int
    _prev: str | None
    _next: str | None
