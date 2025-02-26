from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_player_award_comp_season_response import (
    PulseliveTeamsCompseasonsStaffPlayerAwardCompSeasonResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_player_award_date_response import (
    PulseliveTeamsCompseasonsStaffPlayerAwardDateResponse,
)


class PulseliveTeamsCompseasonsStaffPlayerAwardResponse(CamelCaseModel):
    date: PulseliveTeamsCompseasonsStaffPlayerAwardDateResponse
    comp_season: PulseliveTeamsCompseasonsStaffPlayerAwardCompSeasonResponse
