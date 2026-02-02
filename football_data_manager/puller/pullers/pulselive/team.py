from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.interfaces.pulselive.v1_team import V1TeamsResponse
from football_data_manager.puller.pullers.base import AbstractPuller


class TeamPuller(AbstractPuller[V1TeamsResponse]):
    """Fetches team data from the Pulselive API."""

    def __init__(self, client: PulseliveClient):
        self._client = client

    async def pull_teams(
        self,
        competition_source_id: str,
        season_source_id: str,
        limit: int = 50,
        _next: str | None = None,
    ) -> V1TeamsResponse:
        """Fetch team list by season."""
        return await self._client.get_v1_teams(
            competition_source_id, season_source_id, limit=limit, _next=_next,
        )

    async def close(self) -> None:
        await self._client.close()
