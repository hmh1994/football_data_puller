from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_person_response import (
    PulseliveNewPersonResponse,
)


class PulseliveNewManagerResponse(PulseliveNewPersonResponse):
    id: str
    type: str
