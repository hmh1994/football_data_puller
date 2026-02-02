from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.interfaces.pulselive.v1_player import (
    PlayerDetailResponse,
    V1PlayerDetailsResponse,
    V1PlayerResponse,
)
from football_data_manager.puller.interfaces.pulselive.v2_player import V2SquadResponse
from football_data_manager.puller.pullers.base import AbstractPuller


class PlayerPuller(AbstractPuller[PlayerDetailResponse]):
    """Fetches player data from the Pulselive API."""

    def __init__(self, client: PulseliveClient):
        self._client = client

    async def pull_squad(
        self,
        competition_source_id: str,
        season_source_id: str,
        team_source_id: str,
    ) -> V2SquadResponse:
        """Fetch team squad (player list)."""
        return await self._client.get_v2_squad(
            competition_source_id, season_source_id, team_source_id,
        )

    async def pull_player(self, player_source_id: str) -> V1PlayerResponse:
        """Fetch player detail information."""
        return await self._client.get_v1_player(player_source_id)

    async def pull_player_details(
        self,
        competition_source_id: str,
        season_source_id: str,
        player_source_id: str,
    ) -> V1PlayerDetailsResponse:
        """Fetch player details by season."""
        return await self._client.get_v1_player_details(
            competition_source_id, season_source_id, player_source_id,
        )

    async def close(self) -> None:
        await self._client.close()
