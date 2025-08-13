from typing import Dict

import httpx


class ResourceValidationClient:
    """
    Web client service for validating the existence of web resources.

    Provides functionality to check if URLs exist and are accessible,
    specifically designed for validating team icons and other remote resources.
    Implements caching to avoid repeated checks for the same URLs.

    :ivar __http_client: HTTP client for making validation requests
    :ivar __url_cache: Cache of validated URLs to avoid duplicate checks
    """

    def __init__(self, timeout: float = 10.0):
        """
        Initialize the resource validation client.

        :param timeout: Request timeout in seconds for HTTP requests
        """
        self.__http_client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "FootballDataManager/1.0"},
        )
        self.__url_cache: Dict[str, bool] = {}

    async def validate_url_exists(self, url: str) -> bool:
        """
        Validate that a URL exists and is accessible.

        Makes a HEAD request to check if the resource exists without downloading
        the full content. Caches results to avoid repeated requests for the same URL.

        :param url: URL to validate
        :returns: True if URL exists and is accessible, False otherwise
        """
        # Check cache first
        if url in self.__url_cache:
            return self.__url_cache[url]

        try:
            response = await self.__http_client.head(url)
            exists = response.status_code == 200

            # Cache the result
            self.__url_cache[url] = exists
            return exists

        except (httpx.RequestError, httpx.HTTPStatusError):
            # Cache negative result
            self.__url_cache[url] = False
            return False

    async def close(self):
        """
        Close the HTTP client and clean up resources.

        Should be called when the client is no longer needed to properly
        close HTTP connections and free resources.
        """
        await self.__http_client.aclose()

    def clear_cache(self):
        """
        Clear the URL validation cache.

        Useful for forcing re-validation of URLs that may have changed status.
        """
        self.__url_cache.clear()
