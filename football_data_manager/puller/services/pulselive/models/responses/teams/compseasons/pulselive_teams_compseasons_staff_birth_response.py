from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_country_response import (
    PulseliveTeamsCompseasonsStaffCountryResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_date_response import (
    PulseliveTeamsCompseasonsStaffDateResponse,
)


class PulseliveTeamsCompseasonsStaffBirthResponse(CamelCaseModel):
    date: PulseliveTeamsCompseasonsStaffDateResponse | None = None
    country: PulseliveTeamsCompseasonsStaffCountryResponse
    place: str | None = None
