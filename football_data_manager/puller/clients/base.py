import logging
from typing import Any, TypeVar

from httpx import AsyncClient, URL, Timeout
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)
TModel = TypeVar("TModel", bound=BaseModel)


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

    def _build_url(self, path: str, params: dict[str, Any] | None = None) -> URL:
        url = self._base_url.join(path)
        if params:
            url = url.copy_merge_params(params)
        return url

    @staticmethod
    def _validate_response(
        model: type[TModel],
        response: Any,
        url: URL,
    ) -> TModel:
        try:
            return model.model_validate(response)
        except ValidationError as exc:
            logger.error("Validation error for %s", url, exc_info=exc)
            raise
