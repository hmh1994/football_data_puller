from httpx import URL

from football_data_manager.common.services.client.web_client_service import (
    AbstractWebClientService,
)
from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_list_response import (
    PulseliveNewListResponse,
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
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v2_match_response import (
    PulseliveNewV2MatchResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v3_match_lineup_response import (
    PulseliveNewV3MatchLineupResponse,
)


class PulseliveNewWebclient(AbstractWebClientService):

    def __init__(self, config: ApiConfig):
        super().__init__(URL(config.url.unicode_string()))

    async def get_v2_match(self, match_id: str) -> PulseliveNewV2MatchResponse:
        """
        Get a match by ID.
        :param match_id: Match ID.
        :return: Match information.
        """
        response = await self.get(path=URL(f"v2/matches/{match_id}"))
        return PulseliveNewV2MatchResponse.model_validate(response)

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
