from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.interfaces.pulselive.v1_competition import (
    V1CompetitionDetailResponse,
)
from football_data_manager.puller.pullers.base import AbstractPuller


class SeasonPuller(AbstractPuller[V1CompetitionDetailResponse]):
    """Fetches season data from the Pulselive API."""

    def __init__(self, client: PulseliveClient):
        self._client = client

    async def pull_seasons(
        self, competition_source_id: str,
    ) -> V1CompetitionDetailResponse:
        """Fetch the list of seasons for a competition."""
        return await self._client.get_v1_competition_details(competition_source_id)

    async def close(self) -> None:
        await self._client.close()
