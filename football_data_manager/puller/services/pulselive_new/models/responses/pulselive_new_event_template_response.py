from datetime import datetime

from pydantic import field_validator

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewEventTemplateResponse(CamelCaseModel):
    period: str | None = None
    time: str | None = None
    timestamp: datetime | None = None

    @field_validator("timestamp", mode="before")
    def parse_custom_dt(cls, v) -> datetime | None:
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return datetime.strptime(v, "%Y%m%dT%H%M%S%z")
            except ValueError:
                return None
        return v

    def is_valid_event(self) -> bool:
        """
        Check if the event has all required fields for processing.
        
        :returns: True if event has period, time, and timestamp; False otherwise
        """
        return (
            self.period is not None 
            and self.period.strip() != ""
            and self.time is not None 
            and self.time.strip() != ""
            and self.timestamp is not None
        )
