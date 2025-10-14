from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewAwardCareerResponse(CamelCaseModel):
    """
    Career information for award recipients.

    Contains career statistics including seasons in Premier League
    and seasons at current team.

    :ivar seasons_in_premier_league: List of seasons played in Premier League
    :ivar first_premier_league_fixture_id: ID of first Premier League match
    :ivar seasons_at_current_team: List of seasons at current team
    """

    seasons_in_premier_league: list[str]
    first_premier_league_fixture_id: str
    seasons_at_current_team: list[str]
