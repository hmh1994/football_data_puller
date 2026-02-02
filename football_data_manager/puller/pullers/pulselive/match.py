from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.interfaces.pulselive.v1_match import (
    V1EventResponse,
    V1MatchOfficialsResponse,
)
from football_data_manager.puller.interfaces.pulselive.v2_match import (
    V2MatchResponse,
    V3MatchLineupResponse,
)
from football_data_manager.puller.pullers.base import AbstractPuller


class MatchPuller(AbstractPuller[V2MatchResponse]):
    """Fetches match detail data from the Pulselive API."""

    def __init__(self, client: PulseliveClient):
        self._client = client

    async def pull_match(self, match_source_id: str) -> V2MatchResponse:
        """Fetch match detail information."""
        return await self._client.get_v2_match(match_source_id)

    async def pull_match_event(self, match_source_id: str) -> V1EventResponse:
        """Fetch match events (goals, cards, substitutions)."""
        return await self._client.get_v1_match_event(match_source_id)

    async def pull_match_official(
        self, match_source_id: str,
    ) -> V1MatchOfficialsResponse:
        """Fetch match official information."""
        return await self._client.get_v1_match_official(match_source_id)

    async def pull_match_lineup(
        self, match_source_id: str,
    ) -> V3MatchLineupResponse:
        """Fetch match lineup."""
        return await self._client.get_v3_match_lineup(match_source_id)

    async def close(self) -> None:
        await self._client.close()
