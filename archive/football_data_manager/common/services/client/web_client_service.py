from abc import ABCMeta
from typing import Any

from httpx import AsyncClient, Timeout, URL


class AbstractWebClientService(metaclass=ABCMeta):
    """
    Abstract class for web client services.
    :param base_url: Base URL of the API.
    :param timeout: Timeout for the requests.
    """

    base_url: URL
    timeout: Timeout
    __client: AsyncClient

    def __init__(self, base_url: URL, timeout: Timeout = Timeout(10)):
        self.base_url = base_url
        self.timeout = timeout
        self.__client = AsyncClient(base_url=base_url)

    async def close(self):
        """
        Closes the web client.
        """
        if self.__client:
            await self.__client.aclose()

    async def get(
        self,
        path: URL,
        query: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> dict | None:
        """
        Sends a GET request to the API.

        :param path: Sub-path of the API.
        :param query: Query parameters.
        :param headers: Headers.
        :returns: Response from the API, or None if response body is empty.
        """
        response = await self.__client.get(
            url=self.base_url.join(path),
            params=query if query else {},
            headers=headers if headers else {},
            timeout=self.timeout,
        )
        print("GET request to:", response.url)
        response.raise_for_status()
        if not response.text:
            return None
        return response.json()

    async def post(
        self,
        path: URL,
        query: dict[str, Any] | None = None,
        data: Any = None,
        json: dict | None = None,
        headers: dict[str, Any] | None = None,
    ) -> dict:
        """
        Sends a POST request to the API.
        :param path: Sub-path of the API.
        :param query: Query parameters.
        :param data: Data to send.
        :param json: JSON data to send.
        :param headers: Headers.
        :return: Response from the API.
        """
        response = await self.__client.post(
            url=self.base_url.join(path),
            params=query if query else {},
            data=data,
            json=json,
            headers=headers if headers else {},
            timeout=self.timeout,
        )
        print("POST request to:", response.url, "with body:\n", data or json)
        response.raise_for_status()
        return response.json()
