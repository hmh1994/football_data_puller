from typing import TypedDict


class AuthorDict(TypedDict):
    """Author info. Shared across league_feed and article endpoints."""

    first_name: str
    last_name: str
