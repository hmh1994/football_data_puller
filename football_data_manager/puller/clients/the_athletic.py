import logging
from typing import Any

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from pydantic import ValidationError

from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.puller.interfaces.the_athletic.league_feed import (
    LeagueFeedResponse,
    QueryVariables,
)

logger = logging.getLogger(__name__)


class TheAthleticClient:
    """The Athletic GraphQL API client.

    Executes GraphQL queries using the gql library.
    """

    _LEAGUE_IDS = {"EN_PR": 6}

    _LEAGUE_FEED_QUERY = """
    query LeagueFeedQuery(
        $feed: String!,
        $feed_id: Int!,
        $page: Int!
    ) {
        feedMulligan(
            feed: $feed,
            feed_id: $feed_id,
            page: $page
        ) {
            __typename
            layouts {
                __typename
                type
                typename
                contents {
                    __typename
                    ... on ArticleConsumable {
                        title
                        consumable_id
                        author {
                            first_name
                            last_name
                        }
                        excerpt
                        image_uri
                        permalink
                    }
                }
            }
        }
    }
    """

    def __init__(self, config: ApiConfig | dict):
        parsed_config = (
            config if isinstance(config, ApiConfig) else ApiConfig.model_validate(config)
        )
        self._url = parsed_config.url.unicode_string()
        self._transport = AIOHTTPTransport(
            url=self._url,
            timeout=10,
            ssl=False,
        )
        self._client = Client(
            transport=self._transport,
            fetch_schema_from_transport=False,
        )

    async def get_league_feed(
        self, league_abbr: str, page: int,
    ) -> LeagueFeedResponse:
        variables = QueryVariables(
            feed_id=self._LEAGUE_IDS[league_abbr],
            page=page,
        )
        result = await self._execute(
            query=self._LEAGUE_FEED_QUERY,
            variables=variables.model_dump(),
            operation_name="LeagueFeedQuery",
        )
        try:
            return LeagueFeedResponse.model_validate(result)
        except ValidationError as exc:
            logger.error("Validation error for %s", self._url, exc_info=exc)
            raise

    async def _execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict:
        document = gql(query)
        async with self._client as session:
            return await session.execute(
                document,
                variable_values=variables,
                operation_name=operation_name,
            )

    async def close(self) -> None:
        await self._transport.close()
