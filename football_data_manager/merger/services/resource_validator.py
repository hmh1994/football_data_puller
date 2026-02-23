import httpx


class ResourceValidationClient:
    """Validate URL availability with HTTP HEAD and in-memory caching."""

    def __init__(self, timeout: float = 10.0):
        self._client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "FootballDataManager/1.0"},
        )
        self._cache: dict[str, bool] = {}

    async def validate_url_exists(self, url: str) -> bool:
        """Return True only when HEAD responds with HTTP 200."""
        if not url:
            return False
        if url in self._cache:
            return self._cache[url]

        try:
            response = await self._client.head(url)
            exists = response.status_code == 200
        except httpx.HTTPError:
            exists = False

        self._cache[url] = exists
        return exists

    def clear_cache(self) -> None:
        """Reset URL validation cache."""
        self._cache.clear()

    async def close(self) -> None:
        """Close underlying HTTP client."""
        await self._client.aclose()
