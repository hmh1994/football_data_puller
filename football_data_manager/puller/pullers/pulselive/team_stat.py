from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.interfaces.pulselive.v2_team_stat import (
    V2TeamStatsResponse,
)
from football_data_manager.puller.pullers.base import AbstractPuller


class TeamStatPuller(AbstractPuller[V2TeamStatsResponse]):
    """Fetches team statistics from the Pulselive API."""

    def __init__(self, client: PulseliveClient):
        self._client = client

    async def pull_team_stats(
        self,
        competition_source_id: str,
        season_source_id: str,
        team_source_id: str,
    ) -> V2TeamStatsResponse:
        """Fetch team statistics by season."""
        return await self._client.get_v2_team_stats(
            competition_source_id, season_source_id, team_source_id,
        )

    async def close(self) -> None:
        await self._client.close()
