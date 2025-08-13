from httpx import URL

from football_data_manager.common.services.client.web_client_service import (
    AbstractWebClientService,
)
from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_list_response import (
    PulseliveNewListResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_competition_detail_response import (
    PulseliveNewV1CompetitionDetailResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_competition_response import (
    PulseliveNewV1CompetitionResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_event_response import (
    PulseliveNewV1EventResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_match_officials_response import (
    PulseliveNewV1MatchOfficialsResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_match_team_stat_response import (
    PulseliveNewV1MatchTeamStatResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_matchweek_matches_response import (
    PulseliveNewV1MatchweekMatchesResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v1_teams_response import (
    PulseliveNewV1TeamsResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v2_match_response import (
    PulseliveNewV2MatchResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v2_squad_response import (
    PulseliveNewV2SquadResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v3_match_lineup_response import (
    PulseliveNewV3MatchLineupResponse,
)


class PulseliveNewWebclient(AbstractWebClientService):

    def __init__(self, config: ApiConfig):
        super().__init__(URL(config.url.unicode_string()))

    async def get_v1_competitions(
        self, limit: int = 10, _next: str | None = None
    ) -> PulseliveNewV1CompetitionResponse:
        """
        Get competitions list.

        :param limit: Maximum number of competitions to return (default: 10)
        :param _next: Pagination cursor for next page (optional)
        :returns: Competition list with pagination information
        """
        params = {"_limit": str(limit)}
        if _next:
            params["_next"] = _next

        response = await self.get(path=URL("v1/competitions"), query=params)
        return PulseliveNewV1CompetitionResponse.model_validate(response)

    async def get_v1_competition_details(
        self, competition_id: str
    ) -> PulseliveNewV1CompetitionDetailResponse:
        """
        Get competition details including all seasons.

        :param competition_id: Competition ID to fetch details for
        :returns: Competition details with seasons list
        """
        response = await self.get(path=URL(f"v1/competitions/{competition_id}/details"))
        return PulseliveNewV1CompetitionDetailResponse.model_validate(response)

    async def get_v1_matchweek_matches(
        self,
        competition_id: str,
        season_id: str,
        matchweek_number: int,
        limit: int = 50,
        _next: str | None = None,
    ) -> PulseliveNewV1MatchweekMatchesResponse:
        """
        Get matches for a specific matchweek.

        :param competition_id: Competition ID
        :param season_id: Season ID
        :param matchweek_number: Matchweek number to fetch
        :param limit: Maximum number of matches to return
        :param _next: Pagination cursor for next page
        :returns: Matches for the specified matchweek
        """
        params = {"_limit": str(limit)}
        if _next:
            params["_next"] = _next

        path = f"v1/competitions/{competition_id}/seasons/{season_id}/matchweeks/{matchweek_number}/matches"
        response = await self.get(path=URL(path), query=params)
        return PulseliveNewV1MatchweekMatchesResponse.model_validate(response)

    async def get_v1_match_event(self, match_id: str) -> PulseliveNewV1EventResponse:
        """
        Get a match event by ID.
        :param match_id: Match ID.
        :return: Match event information.
        """
        response = await self.get(path=URL(f"v1/matches/{match_id}/events"))
        return PulseliveNewV1EventResponse.model_validate(response)

    async def get_v1_match_official(
        self, match_id: str
    ) -> PulseliveNewV1MatchOfficialsResponse:
        """
        Get a match official by ID.
        :param match_id: Match ID.
        :return: Match official information.
        """
        response = await self.get(path=URL(f"v1/matches/{match_id}/officials"))
        return PulseliveNewV1MatchOfficialsResponse.model_validate(response)

    async def get_v1_match_stat(
        self, match_id: str
    ) -> list[PulseliveNewV1MatchTeamStatResponse]:
        """
        Get a match stat.
        :param match_id: Match ID.
        :return: Match stat for each team.
        """
        response = await self.get(path=URL(f"v1/matches/{match_id}/stats"))
        return (
            PulseliveNewListResponse[PulseliveNewV1MatchTeamStatResponse]
            .model_validate(response)
            .root
        )

    async def get_v1_teams(
        self,
        competition_id: str,
        season_id: str,
        limit: int = 50,
        _next: str | None = None,
    ) -> PulseliveNewV1TeamsResponse:
        """
        Get teams for a specific competition season.

        :param competition_id: Competition ID
        :param season_id: Season ID
        :param limit: Maximum number of teams to return
        :param _next: Pagination cursor for next page
        :returns: Teams with stadium information for the specified season
        """
        params = {"_limit": str(limit)}
        if _next:
            params["_next"] = _next

        path = f"v1/competitions/{competition_id}/seasons/{season_id}/teams"
        response = await self.get(path=URL(path), query=params)
        return PulseliveNewV1TeamsResponse.model_validate(response)

    async def get_v2_match(self, match_id: str) -> PulseliveNewV2MatchResponse:
        """
        Get a match by ID.
        :param match_id: Match ID.
        :return: Match information.
        """
        response = await self.get(path=URL(f"v2/matches/{match_id}"))
        return PulseliveNewV2MatchResponse.model_validate(response)

    async def get_v2_squad(
        self,
        competition_id: str,
        season_id: str,
        team_id: str,
    ) -> PulseliveNewV2SquadResponse:
        """
        Get squad information for a specific team in a competition season.

        Retrieves player squad data including personal information, positions,
        and physical attributes for the specified team.

        :param competition_id: Competition ID
        :param season_id: Season ID
        :param team_id: Team ID
        :returns: Squad information with player details
        """
        path = f"v2/competitions/{competition_id}/seasons/{season_id}/teams/{team_id}/squad"
        response = await self.get(path=URL(path))
        return PulseliveNewV2SquadResponse.model_validate(response)

    async def get_v3_match_lineup(
        self, match_id: str
    ) -> PulseliveNewV3MatchLineupResponse:
        """
        Get a match lineup by ID.
        :param match_id: Match ID.
        :return: Match lineup information.
        """
        response = await self.get(path=URL(f"v3/matches/{match_id}/lineups"))
        return PulseliveNewV3MatchLineupResponse.model_validate(response)
