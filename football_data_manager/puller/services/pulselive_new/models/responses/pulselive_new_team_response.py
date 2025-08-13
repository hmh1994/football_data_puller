from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_stadium_response import (
    PulseliveNewStadiumResponse,
)


class PulseliveNewTeamResponse(CamelCaseModel):
    """
    Team information from PulseLive teams API response.

    Contains team details including names, abbreviations, and stadium
    information for teams in a specific competition season.
    """

    id: str
    name: str
    short_name: str | None = None
    abbr: str
    stadium: PulseliveNewStadiumResponse
