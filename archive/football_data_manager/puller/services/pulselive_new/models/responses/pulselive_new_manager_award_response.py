from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_award_base_response import (
    PulseliveNewAwardBaseResponse,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_award_career_response import (
    PulseliveNewAwardCareerResponse,
)


class PulseliveNewManagerAwardResponse(PulseliveNewAwardBaseResponse):
    """
    Manager award information from PulseLive v1 awards API.

    Extends PulseliveNewAwardBaseResponse with manager-specific fields including
    career statistics and role information.

    :ivar id: Manager identifier (inherited)
    :ivar current_team: Current team information (inherited)
    :ivar date: Award date in YYYY-M format (inherited)
    :ivar country: Nationality information (inherited)
    :ivar name: Manager name information (inherited)
    :ivar dates: Important dates (birth, joined club) (inherited)
    :ivar type: Award type - 'MOTM' (Manager of the Month), 'MOTS' (Manager of the Season) (inherited)
    :ivar career: Career statistics
    :ivar role: Role description (e.g., 'Manager')
    """

    career: PulseliveNewAwardCareerResponse
    role: str
