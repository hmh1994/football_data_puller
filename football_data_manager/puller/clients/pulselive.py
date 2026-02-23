from pydantic import RootModel

from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.puller.clients.base import AbstractWebClient
from football_data_manager.puller.interfaces.pulselive.v1_award import V1AwardResponse
from football_data_manager.puller.interfaces.pulselive.v1_competition import (
    V1CompetitionDetailResponse,
    V1CompetitionResponse,
)
from football_data_manager.puller.interfaces.pulselive.v1_match import (
    V1EventResponse,
    V1MatchOfficialsResponse,
    V1MatchTeamStatResponse,
    V1MatchweekMatchesResponse,
)
from football_data_manager.puller.interfaces.pulselive.v1_player import (
    V1PlayerDetailsResponse,
    V1PlayerResponse,
)
from football_data_manager.puller.interfaces.pulselive.v1_team import V1TeamsResponse
from football_data_manager.puller.interfaces.pulselive.v2_match import (
    V2MatchResponse,
    V3MatchLineupResponse,
)
from football_data_manager.puller.interfaces.pulselive.v2_player import (
    V2PlayerStatResponse,
    V2SquadResponse,
)
from football_data_manager.puller.interfaces.pulselive.v2_team_stat import (
    V2TeamStatsResponse,
)


class PulseliveClient(AbstractWebClient):
    """HTTP client for the Pulselive API.

    Provides methods for v1/v2/v3 endpoints.
    """

    def __init__(self, config: ApiConfig | dict):
        parsed_config = (
            config
            if isinstance(config, ApiConfig)
            else ApiConfig.model_validate(config)
        )
        super().__init__(base_url=parsed_config.url.unicode_string())

    # --- v1 endpoints ---

    async def get_v1_awards(
        self,
        competition_id: str,
        season_id: str,
    ) -> V1AwardResponse:
        path = f"v1/competitions/{competition_id}/seasons/{season_id}/awards"
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(V1AwardResponse, response, url)

    async def get_v1_competitions(
        self,
        limit: int = 10,
        _next: str | None = None,
    ) -> V1CompetitionResponse:
        params = {"_limit": str(limit)}
        if _next:
            params["_next"] = _next
        path = "v1/competitions"
        url = self._build_url(path, params)
        response = await self.get(path=path, params=params)
        return self._validate_response(V1CompetitionResponse, response, url)

    async def get_v1_competition_details(
        self,
        competition_id: str,
    ) -> V1CompetitionDetailResponse:
        path = f"v1/competitions/{competition_id}/details"
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(V1CompetitionDetailResponse, response, url)

    async def get_v1_matchweek_matches(
        self,
        competition_id: str,
        season_id: str,
        matchweek_number: int,
        limit: int = 50,
        _next: str | None = None,
    ) -> V1MatchweekMatchesResponse:
        params = {"_limit": str(limit)}
        if _next:
            params["_next"] = _next
        path = f"v1/competitions/{competition_id}/seasons/{season_id}/matchweeks/{matchweek_number}/matches"
        url = self._build_url(path, params)
        response = await self.get(path=path, params=params)
        return self._validate_response(V1MatchweekMatchesResponse, response, url)

    async def get_v1_match_event(self, match_id: str) -> V1EventResponse:
        path = f"v1/matches/{match_id}/events"
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(V1EventResponse, response, url)

    async def get_v1_match_official(
        self,
        match_id: str,
    ) -> V1MatchOfficialsResponse:
        path = f"v1/matches/{match_id}/officials"
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(V1MatchOfficialsResponse, response, url)

    async def get_v1_match_stat(
        self,
        match_id: str,
    ) -> list[V1MatchTeamStatResponse]:
        path = f"v1/matches/{match_id}/stats"
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(
            RootModel[list[V1MatchTeamStatResponse]], response, url
        ).root

    async def get_v1_teams(
        self,
        competition_id: str,
        season_id: str,
        limit: int = 50,
        _next: str | None = None,
    ) -> V1TeamsResponse:
        params = {"_limit": str(limit)}
        if _next:
            params["_next"] = _next
        path = f"v1/competitions/{competition_id}/seasons/{season_id}/teams"
        url = self._build_url(path, params)
        response = await self.get(path=path, params=params)
        return self._validate_response(V1TeamsResponse, response, url)

    async def get_v1_player(self, player_id: str) -> V1PlayerResponse:
        path = f"v1/players/{player_id}"
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(V1PlayerResponse, response, url)

    async def get_v1_player_details(
        self,
        competition_id: str,
        season_id: str,
        player_id: str,
    ) -> V1PlayerDetailsResponse:
        path = (
            f"v1/competitions/{competition_id}/seasons/{season_id}/players/{player_id}"
        )
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(V1PlayerDetailsResponse, response, url)

    # --- v2 endpoints ---

    async def get_v2_player_stats(
        self,
        competition_id: str,
        season_id: str,
        player_id: str,
    ) -> V2PlayerStatResponse:
        path = f"v2/competitions/{competition_id}/seasons/{season_id}/players/{player_id}/stats"
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(V2PlayerStatResponse, response, url)

    async def get_v2_match(self, match_id: str) -> V2MatchResponse:
        path = f"v2/matches/{match_id}"
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(V2MatchResponse, response, url)

    async def get_v2_squad(
        self,
        competition_id: str,
        season_id: str,
        team_id: str,
    ) -> V2SquadResponse:
        path = f"v2/competitions/{competition_id}/seasons/{season_id}/teams/{team_id}/squad"
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(V2SquadResponse, response, url)

    async def get_v2_team_stats(
        self,
        competition_id: str,
        season_id: str,
        team_id: str,
    ) -> V2TeamStatsResponse:
        path = f"v2/competitions/{competition_id}/seasons/{season_id}/teams/{team_id}/stats"
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(V2TeamStatsResponse, response, url)

    # --- v3 endpoints ---

    async def get_v3_match_lineup(self, match_id: str) -> V3MatchLineupResponse:
        path = f"v3/matches/{match_id}/lineups"
        url = self._build_url(path)
        response = await self.get(path=path)
        return self._validate_response(V3MatchLineupResponse, response, url)
