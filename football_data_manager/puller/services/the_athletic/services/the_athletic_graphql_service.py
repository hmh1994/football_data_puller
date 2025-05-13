from football_data_manager.common.services.client.graphql_client_service import AbstractGraphQLClientService
from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.puller.services.the_athletic.models.requests.the_athletic_query_variables import \
    TheAthleticQueryVariables
from football_data_manager.puller.services.the_athletic.models.responses.the_athletic_league_feed_response import \
    TheAthleticLeagueFeedResponse


class TheAthleticGraphQLService(AbstractGraphQLClientService):
    __league_id = {
        "EN_PR": 6,
    }

    __league_feed_query = """
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

    def __init__(self, api_config: ApiConfig):
        super().__init__(endpoint=api_config.url.unicode_string())

    async def get_league_feed(self, league_abbr: str, page: int) -> TheAthleticLeagueFeedResponse:
        """
        Fetches the league feed from The Athletic API.

        :param league_abbr: League abbreviation.
        :param page: Page number.
        :return: TheAthleticLeagueFeedResponse object.
        """
        variables = self.__gen_variables(league_abbr, page)
        response = await self._execute(
            operation_name="LeagueFeedQuery",
            query=self.__league_feed_query,
            variables=variables.model_dump(),
        )
        return TheAthleticLeagueFeedResponse.model_validate(response)

    def __gen_variables(self, league_abbr: str, page: int) -> TheAthleticQueryVariables:
        """
        Generates the variables for the GraphQL query.

        :param league_abbr: League abbreviation.
        :param page: Page number.
        :return: Dictionary of variables.
        """
        return TheAthleticQueryVariables(
            feed_id=self.__league_id[league_abbr],
            page=page,
        )
