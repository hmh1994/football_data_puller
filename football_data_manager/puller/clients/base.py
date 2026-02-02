from typing import Any

from httpx import AsyncClient, URL, Timeout


class AbstractWebClient:
    """Abstract async HTTP client base class.

    Wraps httpx AsyncClient to provide GET/POST request methods.
    """

    def __init__(self, base_url: str, timeout: float = 10.0):
        self._base_url = URL(base_url)
        self._timeout = Timeout(timeout)
        self._client = AsyncClient(base_url=self._base_url, timeout=self._timeout)

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> dict | None:
        response = await self._client.get(
            path,
            params=params or {},
            headers=headers or {},
        )
        response.raise_for_status()
        if not response.text:
            return None
        return response.json()

    async def post(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        data: Any = None,
        json: dict | None = None,
        headers: dict[str, Any] | None = None,
    ) -> dict:
        response = await self._client.post(
            path,
            params=params or {},
            data=data,
            json=json,
            headers=headers or {},
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self._client.aclose()
