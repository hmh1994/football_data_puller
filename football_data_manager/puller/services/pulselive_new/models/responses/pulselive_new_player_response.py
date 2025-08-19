from datetime import datetime

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.common.utils.type_helper.datetime_helper import (
    parse_date_string_to_utc,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_country_response import (
    PulseliveNewCountryResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_person_response import (
    PulseliveNewPersonResponse,
)


class PulseliveNewPlayerDatesResponse(CamelCaseModel):
    """
    Date information for a player in the squad response.

    Contains important dates for the player including birth and club joining dates
    from the PulseLive v2 squad API response.

    :ivar joined_club: Date when player joined the current club
    :ivar birth: Player's date of birth
    """

    joined_club: str
    birth: datetime | None = None

    @field_validator("birth", mode="before")
    def parse_birth_date(cls, v) -> datetime | None:
        """Parse birth date from string format to UTC datetime."""
        if isinstance(v, str):
            try:
                return parse_date_string_to_utc(v)
            except ValueError:
                return None
        return v


class PulseliveNewPlayerIdResponse(CamelCaseModel):
    competition_id: str | None = None
    season_id: str | None = None
    player_id: str


class PulseliveNewPlayerResponse(CamelCaseModel):
    """
    Individual player information from PulseLive v2 squad API response.

    Contains comprehensive player details including personal information,
    physical attributes, position data, and club information.

    :ivar country: Player's country/nationality information
    :ivar loan: Loan status (0 = permanent, 1 = on loan)
    :ivar country_of_birth: Birth country name
    :ivar name: Player's name information (first, last, display)
    :ivar shirt_num: Jersey/shirt number
    :ivar weight: Player weight in kilograms
    :ivar dates: Important dates (birth, joined club)
    :ivar id: Unique player identifier
    :ivar position: Player position
    :ivar preferred_foot: Preferred foot (Left/Right)
    :ivar height: Player height in centimeters
    """

    country: PulseliveNewCountryResponse | None = None
    loan: int | None = None
    country_of_birth: str | None = None
    name: PulseliveNewPersonResponse
    shirt_num: int | None = None
    weight: int | None = None
    dates: PulseliveNewPlayerDatesResponse
    id: PulseliveNewPlayerIdResponse
    position: str
    preferred_foot: str | None = None
    height: int | None = None

    @field_validator("id", mode="before")
    def parse_id(cls, v) -> PulseliveNewPlayerIdResponse:
        """Parse id."""
        if isinstance(v, str):
            return PulseliveNewPlayerIdResponse(player_id=v)
        return v
