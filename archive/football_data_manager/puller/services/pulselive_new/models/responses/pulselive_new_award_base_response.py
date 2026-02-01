from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_award_dates_response import (
    PulseliveNewAwardDatesResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_award_team_response import (
    PulseliveNewAwardTeamResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_country_response import (
    PulseliveNewCountryResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_person_response import (
    PulseliveNewPersonResponse,
)


class PulseliveNewAwardBaseResponse(CamelCaseModel):
    """
    Base class for award recipients (managers and players).

    Contains common fields shared by all award recipient types including
    identification, team affiliation, nationality, and award metadata.

    :ivar id: Award recipient identifier
    :ivar current_team: Current team information
    :ivar date: Award date in YYYY-M format
    :ivar country: Nationality information
    :ivar name: Recipient name information
    :ivar dates: Important dates (birth, joined club)
    :ivar type: Award type (e.g., 'MOTM', 'POTM', 'GOTM', 'SOTM', 'MOTS')
    """

    id: str
    current_team: PulseliveNewAwardTeamResponse
    date: str
    country: PulseliveNewCountryResponse
    name: PulseliveNewPersonResponse
    dates: PulseliveNewAwardDatesResponse
    type: str
