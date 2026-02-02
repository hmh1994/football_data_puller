from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.interfaces.pulselive.v1_match import (
    V1MatchweekMatchesResponse,
)
from football_data_manager.puller.pullers.base import AbstractPuller


class FixturePuller(AbstractPuller[V1MatchweekMatchesResponse]):
    """Fetches fixture data from the Pulselive API."""

    def __init__(self, client: PulseliveClient):
        self._client = client

    async def pull_matchweek_matches(
        self,
        competition_source_id: str,
        season_source_id: str,
        matchweek_number: int,
        limit: int = 50,
        _next: str | None = None,
    ) -> V1MatchweekMatchesResponse:
        """Fetch match list by matchweek."""
        return await self._client.get_v1_matchweek_matches(
            competition_source_id,
            season_source_id,
            matchweek_number,
            limit=limit,
            _next=_next,
        )

    async def close(self) -> None:
        await self._client.close()
