from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_comp_season_response import (
    PulseliveTeamsCompseasonsStaffCompSeasonResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_official_response import (
    PulseliveTeamsCompseasonsStaffOfficialResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_player_response import (
    PulseliveTeamsCompseasonsStaffPlayerResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_team_response import (
    PulseliveTeamsCompseasonsStaffTeamResponse,
)


class PulseliveTeamsCompseasonsStaffResponse(CamelCaseModel):
    comp_season: PulseliveTeamsCompseasonsStaffCompSeasonResponse
    team: PulseliveTeamsCompseasonsStaffTeamResponse
    players: list[PulseliveTeamsCompseasonsStaffPlayerResponse]
    officials: list[PulseliveTeamsCompseasonsStaffOfficialResponse]
