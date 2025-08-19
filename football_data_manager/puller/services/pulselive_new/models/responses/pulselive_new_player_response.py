from pydantic import field_validator, ValidationInfo

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
    short_name: str


class PulseliveNewPlayerIdResponse(CamelCaseModel):
    competition_id: str | None = None
    season_id: str | None = None
    player_id: str


class PulseliveNewPlayerResponse(CamelCaseModel):
    country: PulseliveNewCountryResponse | None = None
    current_team: PulseliveNewPlayerTeamResponse
    id: PulseliveNewPlayerIdResponse
    name: PulseliveNewPersonResponse
    position: str

    @field_validator("id", mode="before")
    def parse_id(cls, v) -> PulseliveNewPlayerIdResponse:
        """Parse id."""
        if isinstance(v, str):
            return PulseliveNewPlayerIdResponse(player_id=v)
        return v

    @field_validator("name", mode="before")
    def parse_name(cls, v, info: ValidationInfo) -> PulseliveNewPersonResponse:
        """
        Parse name fields into PulseliveNewPersonResponse object.

        Combines firstName, lastName, and name from the raw data into a single
        PulseliveNewPersonResponse object for structured name handling.
        """
        # If v is already a PulseliveNewPersonResponse, return it
        if isinstance(v, PulseliveNewPersonResponse):
            return v

        # Get all field values from the validation context
        all_values = info.data

        # Extract name components from raw data
        first_name = all_values.get("firstName", "")
        last_name = all_values.get("lastName", "")
        display_name = v if isinstance(v, str) else all_values.get("name")

        # Create PulseliveNewPersonResponse object
        return PulseliveNewPersonResponse(
            first_name=first_name, last_name=last_name, display_name=display_name
        )
