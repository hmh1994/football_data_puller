from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.interfaces.pulselive.v2_player import (
    V2PlayerStatResponse,
)
from football_data_manager.puller.pullers.base import AbstractPuller


class PlayerStatPuller(AbstractPuller[V2PlayerStatResponse]):
    """Fetches player statistics from the Pulselive API."""

    def __init__(self, client: PulseliveClient):
        self._client = client

    async def pull_player_stats(
        self,
        competition_source_id: str,
        season_source_id: str,
        player_source_id: str,
    ) -> V2PlayerStatResponse:
        """Fetch player statistics by season."""
        return await self._client.get_v2_player_stats(
            competition_source_id, season_source_id, player_source_id,
        )

    async def close(self) -> None:
        await self._client.close()
