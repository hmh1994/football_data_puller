from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_match_team_response import (
    PulseliveNewMatchTeamResponse,
)


class PulseliveNewMatchResponse(CamelCaseModel):
    """
    Response model for individual match data in matchweeks.

    Contains comprehensive match information including teams, timing,
    venue, and result details from the PulseLive v1 matchweeks API.

    :ivar kickoff_timezone: Timezone of the match kickoff time
    :ivar period: Match period status (e.g., "FullTime", "HalfTime")
    :ivar kickoff: Match kickoff date and time string
    :ivar away_team: Away team information and statistics
    :ivar home_team: Home team information and statistics
    :ivar competition: Competition name
    :ivar ground: Venue name and location
    :ivar clock: Match clock time in minutes
    :ivar result_type: Type of match result
    :ivar match_id: Unique match identifier
    :ivar attendance: Number of attendees
    """

    kickoff_timezone: str
    period: str
    kickoff: str
    away_team: PulseliveNewMatchTeamResponse
    home_team: PulseliveNewMatchTeamResponse
    competition: str
    ground: str | None = None
    clock: str | None = None
    result_type: str | None = None
    match_id: str
    attendance: int | None = None
