from httpx import URL

from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.common.services.web_client.web_client_service import (
    AbstractWebClientService,
)
from football_data_manager.puller.services.pulselive.models.responses.competitions.pulselive_competition_response import (
    PulseliveCompetitionResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.compseasons.gameweeks.pulselive_compseason_gameweek_response import (
    PulseliveCompSeasonGameweekResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.compseasons.teams.pulselive_compseason_team_response import (
    PulseliveCompseasonTeamResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_response import (
    PulseliveFixtureResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.pulselive_list_response import (
    PulseliveListResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.pulselive_paginated_response import (
    PulselivePaginatedResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_response import (
    PulseliveStandingsResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_response import (
    PulseliveTeamsCompseasonsStaffResponse,
)


class PulseliveWebClientService(AbstractWebClientService):
    """
    Service class to handle Pulselive API web client.
    """

    def __init__(self, config: ApiConfig):
        super().__init__(URL(config.url.unicode_string()))

    async def get_football_competitions(
        self,
    ) -> list[PulseliveCompetitionResponse]:
        """
        Get the competitions.
        :return: Competitions.
        """
        response = await self.get(
            path=URL("/football/competitions/"),
            query={"page": "0", "pageSize": "1000", "detail": "2"},
        )
        return (
            PulselivePaginatedResponse[PulseliveCompetitionResponse]
            .model_validate(response)
            .content
        )

    async def get_football_compseasons_gameweeks(
        self, compseason_id: int
    ) -> PulseliveCompSeasonGameweekResponse:
        response = await self.get(
            path=URL(f"/football/compseasons/{compseason_id}/gameweeks"),
        )
        return PulseliveCompSeasonGameweekResponse.model_validate(response)

    async def get_football_compseasons_teams(
        self, compseason_id: int
    ) -> list[PulseliveCompseasonTeamResponse]:
        """
        Get the teams of a competition season.
        :param compseason_id: Competition season ID.
        :return: Teams.
        """
        response = await self.get(
            path=URL(f"/football/compseasons/{compseason_id}/teams"),
            query={
                "altIds": True,
            },
        )
        return (
            PulseliveListResponse[PulseliveCompseasonTeamResponse]
            .model_validate(response)
            .root
        )

    async def get_football_fixtures(
        self, competition_id: int, comp_season_id: int, page: int = 0
    ) -> list[PulseliveFixtureResponse]:
        """
        Gets the fixtures of a competition season.
        :param competition_id: The competition ID of the fixtures.
        :param comp_season_id: The competition season ID of the fixtures.
        :param page: The page number of the fixtures.
        :return: The fixtures of the competition season.
        """
        print(
            f"Getting fixtures for competition {competition_id} and compseason {comp_season_id} on page {page}"
        )
        response = await self.get(
            path=URL("/football/fixtures"),
            query={
                "comps": competition_id,
                "compSeasons": comp_season_id,
                "page": page,
                "pageSize": 10,
                "altIds": True,
                "fast": False,
            },
        )
        return (
            PulselivePaginatedResponse[PulseliveFixtureResponse]
            .model_validate(response)
            .content
        )

    async def get_football_standings(
        self, comp_season_id: int, competition_id: int
    ) -> PulseliveStandingsResponse:
        """
        Get the standings of a competition season.
        :param comp_season_id: Competition season ID.
        :param competition_id: Competition ID.
        :return: Standings.
        """
        response = await self.get(
            path=URL(f"/football/standings"),
            query={
                "FOOTBALL_COMPETITION": competition_id,
                "compSeasons": comp_season_id,
                "altIds": True,
                "detail": 2,
            },
        )
        return PulseliveStandingsResponse.model_validate(response)

    async def get_football_team_compseason_staff(
        self,
        comp_season_id: int,
        team_id: int,
    ) -> PulseliveTeamsCompseasonsStaffResponse:
        response = await self.get(
            path=URL(f"/football/teams/{team_id}/compseasons/{comp_season_id}/staff"),
            query={
                "compSeasons": comp_season_id,
                "altIds": True,
            },
        )
        return PulseliveTeamsCompseasonsStaffResponse.model_validate(response)
