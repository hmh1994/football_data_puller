from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_event_template_response import (
    PulseliveNewEventTemplateResponse,
)


class PulseliveNewEventSubResponse(PulseliveNewEventTemplateResponse):
    player_on_id: str | None = None
    player_off_id: str | None = None

    def is_valid_event(self) -> bool:
        return (
            super().is_valid_event()
            and self.player_on_id is not None
            and self.player_off_id is not None
        )
