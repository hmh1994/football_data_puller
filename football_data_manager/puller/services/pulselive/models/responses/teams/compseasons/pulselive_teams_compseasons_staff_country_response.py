from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveTeamsCompseasonsStaffCountryResponse(CamelCaseModel):
    iso_code: str
    country: str
    demonym: str | None = None
