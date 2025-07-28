from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_event_template_response import (
    PulseliveNewEventTemplateResponse,
)


class PulseliveNewEventSubResponse(PulseliveNewEventTemplateResponse):
    player_on_id: str
    player_off_id: str
