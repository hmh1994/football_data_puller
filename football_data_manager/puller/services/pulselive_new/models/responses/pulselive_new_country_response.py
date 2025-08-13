from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewCountryResponse(CamelCaseModel):
    """
    Country information for a player in the squad response.

    Contains country details including ISO code, name, and demonym
    from the PulseLive v2 squad API response.

    :ivar iso_code: ISO country code (e.g., 'ES', 'BR')
    :ivar country: Country name in English
    :ivar demonym: Demonym for the country (e.g., 'Spanish', 'Brazilian')
    """

    iso_code: str
    country: str
    demonym: str | None = None
