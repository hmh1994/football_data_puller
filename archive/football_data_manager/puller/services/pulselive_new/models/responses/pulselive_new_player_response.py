from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_country_response import (
    PulseliveNewCountryResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_person_response import (
    PulseliveNewPersonResponse,
)


class PulseliveNewPlayerTeamResponse(CamelCaseModel):
    name: str
    id: str
    short_name: str | None = None


class PulseliveNewPlayerIdResponse(CamelCaseModel):
    competition_id: str | None = None
    season_id: str | None = None
    player_id: str


class PulseliveNewPlayerResponse(CamelCaseModel):
    """
    Base player response from PulseLive API.

    Contains basic player information including ID, name, position, and country details
    used across different PulseLive endpoints.

    :ivar id: Player ID response containing player_id
    :ivar position: Player position (e.g., 'Goalkeeper', 'Defender', 'Midfielder', 'Forward')
    :ivar country: Country information including ISO code and name
    :ivar name: Person name information
    """

    country: PulseliveNewCountryResponse
    current_team: PulseliveNewPlayerTeamResponse | None = None
    id: PulseliveNewPlayerIdResponse
    name: PulseliveNewPersonResponse
    position: str

    @field_validator("id", mode="before")
    def parse_id(cls, v) -> dict:
        """Parse player ID from string to PulseliveNewPlayerIdResponse format."""
        if isinstance(v, str):
            return {"player_id": v}
        return v
