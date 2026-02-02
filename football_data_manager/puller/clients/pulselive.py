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

    def __init__(self, config: ApiConfig):
        super().__init__(base_url=config.url.unicode_string())

    # --- v1 endpoints ---

    async def get_v1_awards(
        self, competition_id: str, season_id: str,
    ) -> V1AwardResponse:
        path = f"v1/competitions/{competition_id}/seasons/{season_id}/awards"
        response = await self.get(path=path)
        return V1AwardResponse.model_validate(response)

    async def get_v1_competitions(
        self, limit: int = 10, _next: str | None = None,
    ) -> V1CompetitionResponse:
        params = {"_limit": str(limit)}
        if _next:
            params["_next"] = _next
        response = await self.get(path="v1/competitions", params=params)
        return V1CompetitionResponse.model_validate(response)

    async def get_v1_competition_details(
        self, competition_id: str,
    ) -> V1CompetitionDetailResponse:
        response = await self.get(path=f"v1/competitions/{competition_id}/details")
        return V1CompetitionDetailResponse.model_validate(response)

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
        response = await self.get(path=path, params=params)
        return V1MatchweekMatchesResponse.model_validate(response)

    async def get_v1_match_event(self, match_id: str) -> V1EventResponse:
        response = await self.get(path=f"v1/matches/{match_id}/events")
        return V1EventResponse.model_validate(response)

    async def get_v1_match_official(
        self, match_id: str,
    ) -> V1MatchOfficialsResponse:
        response = await self.get(path=f"v1/matches/{match_id}/officials")
        return V1MatchOfficialsResponse.model_validate(response)

    async def get_v1_match_stat(
        self, match_id: str,
    ) -> list[V1MatchTeamStatResponse]:
        response = await self.get(path=f"v1/matches/{match_id}/stats")
        return RootModel[list[V1MatchTeamStatResponse]].model_validate(response).root

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
        response = await self.get(path=path, params=params)
        return V1TeamsResponse.model_validate(response)

    async def get_v1_player(self, player_id: str) -> V1PlayerResponse:
        response = await self.get(path=f"v1/players/{player_id}")
        return V1PlayerResponse.model_validate(response)

    async def get_v1_player_details(
        self, competition_id: str, season_id: str, player_id: str,
    ) -> V1PlayerDetailsResponse:
        path = f"v1/competitions/{competition_id}/seasons/{season_id}/players/{player_id}"
        response = await self.get(path=path)
        return V1PlayerDetailsResponse.model_validate(response)

    # --- v2 endpoints ---

    async def get_v2_player_stats(
        self, competition_id: str, season_id: str, player_id: str,
    ) -> V2PlayerStatResponse:
        path = f"v2/competitions/{competition_id}/seasons/{season_id}/players/{player_id}/stats"
        response = await self.get(path=path)
        return V2PlayerStatResponse.model_validate(response)

    async def get_v2_match(self, match_id: str) -> V2MatchResponse:
        response = await self.get(path=f"v2/matches/{match_id}")
        return V2MatchResponse.model_validate(response)

    async def get_v2_squad(
        self, competition_id: str, season_id: str, team_id: str,
    ) -> V2SquadResponse:
        path = f"v2/competitions/{competition_id}/seasons/{season_id}/teams/{team_id}/squad"
        response = await self.get(path=path)
        return V2SquadResponse.model_validate(response)

    async def get_v2_team_stats(
        self, competition_id: str, season_id: str, team_id: str,
    ) -> V2TeamStatsResponse:
        path = f"v2/competitions/{competition_id}/seasons/{season_id}/teams/{team_id}/stats"
        response = await self.get(path=path)
        return V2TeamStatsResponse.model_validate(response)

    # --- v3 endpoints ---

    async def get_v3_match_lineup(self, match_id: str) -> V3MatchLineupResponse:
        response = await self.get(path=f"v3/matches/{match_id}/lineups")
        return V3MatchLineupResponse.model_validate(response)
