from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewAwardTeamResponse(CamelCaseModel):
    """
    Team information for award recipients.

    Contains team details for players or managers who received awards.
    Note: Unlike PulseliveNewTeamSimpleResponse, the awards API doesn't include
    the abbr field, so this is a separate implementation.

    :ivar id: Team identifier
    :ivar name: Full team name
    :ivar short_name: Abbreviated team name
    :ivar loan: Loan status (0 for permanent, 1 for loan) - only present for players
    """

    id: str
    name: str
    short_name: str
    loan: int | None = None
