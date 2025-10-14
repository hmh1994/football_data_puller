from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewAwardDatesResponse(CamelCaseModel):
    """
    Important dates for award recipients.

    Contains birth date and club joining date information.

    :ivar birth: Birth date in YYYY-MM-DD format
    :ivar joined_club: Club joining date in YYYY-MM-DD format
    """

    birth: str
    joined_club: str
