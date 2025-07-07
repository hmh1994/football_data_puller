from abc import ABCMeta
from typing import Any

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport


class AbstractGraphQLClientService(metaclass=ABCMeta):
    """
    Abstract class for GraphQL client services using gql package.

    :param endpoint: GraphQL endpoint URL.
    :param headers: Optional HTTP headers.
    :param timeout: Timeout in seconds for HTTP requests.
    """

    base_url: str
    headers: dict[str, str]
    timeout: int
    __transport: AIOHTTPTransport
    __client: Client

    def __init__(
        self,
        endpoint: str,
        fetch_schema_from_transport: bool = False,
        headers: dict[str, str] | None = None,
        timeout: int = 10,
    ):
        self.endpoint = endpoint
        self.headers = headers or {}
        self.timeout = timeout
        self.__transport = AIOHTTPTransport(
            url=self.endpoint,
            headers=self.headers,
            timeout=self.timeout,
        )
        self.__client = Client(
            transport=self.__transport,
            fetch_schema_from_transport=fetch_schema_from_transport,
        )

    async def close(self) -> None:
        """
        Closes the underlying transport connection.
        """
        await self.__transport.close()

    async def _execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        """
        Executes a GraphQL query or mutation.

        :param query: The GraphQL query/mutation string.
        :param variables: Optional dict of variables for the operation.
        :param operation_name: Optional name of the operation.
        :return: Response data as a dict.
        """
        document = gql(query)
        async with self.__client as session:
            result = await session.execute(
                document,
                variable_values=variables,
                operation_name=operation_name,
            )
        return result
