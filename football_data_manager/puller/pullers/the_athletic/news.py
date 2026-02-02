from football_data_manager.puller.clients.the_athletic import TheAthleticClient
from football_data_manager.puller.interfaces.the_athletic.league_feed import (
    LeagueFeedResponse,
)
from football_data_manager.puller.pullers.base import AbstractPuller


class NewsPuller(AbstractPuller[LeagueFeedResponse]):
    """Fetches news data from The Athletic."""

    def __init__(self, client: TheAthleticClient):
        self._client = client

    async def pull_league_feed(
        self, league_abbr: str, page: int = 1,
    ) -> LeagueFeedResponse:
        """Fetch news feed by league."""
        return await self._client.get_league_feed(league_abbr, page)

    async def close(self) -> None:
        await self._client.close()
