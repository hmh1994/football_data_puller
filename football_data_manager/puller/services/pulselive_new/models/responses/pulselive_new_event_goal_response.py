from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_event_template_response import (
    PulseliveNewEventTemplateResponse,
)


class PulseliveNewEventGoalResponse(PulseliveNewEventTemplateResponse):
    goal_type: str
    assist_player_id: str
    player_id: str
