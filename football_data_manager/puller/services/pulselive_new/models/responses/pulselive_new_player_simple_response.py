from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_person_response import (
    PulseliveNewPersonResponse,
)


class PulseliveNewPlayerSimpleResponse(PulseliveNewPersonResponse):
    shirt_num: str
    is_captain: bool
    id: str
    position: str
    sub_position: str | None = None
