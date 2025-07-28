from datetime import datetime

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewEventTemplateResponse(CamelCaseModel):
    period: str
    time: str
    timestamp: datetime

    @field_validator("timestamp", mode="before")
    def parse_custom_dt(cls, v) -> datetime:
        if isinstance(v, str):
            return datetime.strptime(v, "%Y%m%dT%H%M%S%z")
        return v
