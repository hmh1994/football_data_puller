from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewMatchTeamResponse(CamelCaseModel):
    """
    Response model for team information in matchweek matches.

    Represents team data including score, name, and match statistics
    from the PulseLive v1 matchweeks API.

    :ivar score: Final team score
    :ivar name: Full team name
    :ivar id: Team identifier
    :ivar half_time_score: Score at half time
    :ivar short_name: Abbreviated team name
    :ivar red_cards: Number of red cards received
    """

    score: int | None = None
    name: str
    id: str
    half_time_score: int | None = None
    short_name: str | None = None
    red_cards: int | None = None
