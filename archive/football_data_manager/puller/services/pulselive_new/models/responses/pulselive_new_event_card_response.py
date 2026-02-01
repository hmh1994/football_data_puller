from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_event_template_response import (
    PulseliveNewEventTemplateResponse,
)


class PulseliveNewEventCardResponse(PulseliveNewEventTemplateResponse):
    type: str
    player_id: str | None = None
