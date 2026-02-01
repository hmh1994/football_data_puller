from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveStandingsTableEntryAnnotationResponse(CamelCaseModel):
    type: str
    destination: str | None = None
    description: str
