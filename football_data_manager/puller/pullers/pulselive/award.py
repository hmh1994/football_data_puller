from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.interfaces.pulselive.v1_award import V1AwardResponse
from football_data_manager.puller.pullers.base import AbstractPuller


class AwardPuller(AbstractPuller[V1AwardResponse]):
    """Fetches award data from the Pulselive API."""

    def __init__(self, client: PulseliveClient):
        self._client = client

    async def pull_awards(
        self, competition_source_id: str, season_source_id: str,
    ) -> V1AwardResponse:
        """Fetch award information by season."""
        return await self._client.get_v1_awards(
            competition_source_id, season_source_id,
        )

    async def close(self) -> None:
        await self._client.close()
