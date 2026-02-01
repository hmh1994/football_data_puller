from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_event_card_response import (
    PulseliveNewEventCardResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_event_goal_response import (
    PulseliveNewEventGoalResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_event_sub_response import (
    PulseliveNewEventSubResponse,
)


class PulseliveNewEventTeamResponse(CamelCaseModel):
    cards: list[PulseliveNewEventCardResponse]
    subs: list[PulseliveNewEventSubResponse]
    name: str
    id: str
    short_name: str
    goals: list[PulseliveNewEventGoalResponse]
