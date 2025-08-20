from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_team_simple_response import (
    PulseliveNewTeamSimpleResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_team_stats_response import (
    PulseliveNewTeamStatsResponse,
)


class PulseliveNewV2TeamStatsResponse(CamelCaseModel):
    """
    Main team statistics response from PulseLive API v2.
    
    Contains team statistics data and basic team information for a specific
    competition season.
    
    :ivar stats: Comprehensive team performance statistics
    :ivar team: Basic team information (id, name, abbreviation)
    """
    
    stats: PulseliveNewTeamStatsResponse
    team: PulseliveNewTeamSimpleResponse