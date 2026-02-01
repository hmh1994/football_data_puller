from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewStadiumResponse(CamelCaseModel):
    """
    Stadium information from PulseLive teams API response.

    Contains stadium details including name, location, and capacity
    for teams in a specific competition season.
    """

    country: str | None = None
    city: str | None = None
    name: str | None = None
    capacity: int | None = None
