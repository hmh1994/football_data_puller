from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.interfaces.pulselive.v1_competition import (
    V1CompetitionDetailResponse,
    V1CompetitionResponse,
)
from football_data_manager.puller.pullers.base import AbstractPuller


class CompetitionPuller(AbstractPuller[V1CompetitionResponse]):
    """Fetches competition data from the Pulselive API."""

    def __init__(self, client: PulseliveClient):
        self._client = client

    async def pull_competitions(
        self, limit: int = 10, _next: str | None = None,
    ) -> V1CompetitionResponse:
        """Fetch the list of competitions."""
        return await self._client.get_v1_competitions(limit=limit, _next=_next)

    async def pull_competition_details(
        self, competition_source_id: str,
    ) -> V1CompetitionDetailResponse:
        """Fetch competition details (including season list)."""
        return await self._client.get_v1_competition_details(competition_source_id)

    async def close(self) -> None:
        await self._client.close()
