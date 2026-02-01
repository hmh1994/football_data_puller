from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_person_response import (
    PulseliveNewPersonResponse,
)


class PulseliveNewManagerResponse(PulseliveNewPersonResponse):
    id: str | None = None
    type: str | None = None

    def is_valid_event(self) -> bool:
        return (
            super().is_valid_event() and self.id is not None and self.type is not None
        )
