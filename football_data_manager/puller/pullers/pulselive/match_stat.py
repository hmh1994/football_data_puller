from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.interfaces.pulselive.v1_match import (
    V1MatchTeamStatResponse,
)
from football_data_manager.puller.pullers.base import AbstractPuller


class MatchStatPuller(AbstractPuller[V1MatchTeamStatResponse]):
    """Fetches match statistics from the Pulselive API."""

    def __init__(self, client: PulseliveClient):
        self._client = client

    async def pull_match_stat(
        self, match_source_id: str,
    ) -> list[V1MatchTeamStatResponse]:
        """Fetch team statistics per match."""
        return await self._client.get_v1_match_stat(match_source_id)

    async def close(self) -> None:
        await self._client.close()
