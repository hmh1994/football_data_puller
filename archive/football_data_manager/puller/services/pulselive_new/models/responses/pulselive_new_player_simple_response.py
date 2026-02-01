from pydantic import field_validator

from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_person_response import (
    PulseliveNewPersonResponse,
)


class PulseliveNewPlayerSimpleResponse(PulseliveNewPersonResponse):
    shirt_num: str
    is_captain: bool = False
    id: str
    position: str
    sub_position: str | None = None

    @field_validator("is_captain", mode="before")
    def parse_is_captain(cls, v) -> bool:
        """Parse is_captain."""
        if isinstance(v, bool):
            return v
        return False
