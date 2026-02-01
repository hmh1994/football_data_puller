from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_award_base_response import (
    PulseliveNewAwardBaseResponse,
)


class PulseliveNewPlayerAwardResponse(PulseliveNewAwardBaseResponse):
    """
    Player award information from PulseLive v1 awards API.

    Extends PulseliveNewAwardBaseResponse with player-specific fields including
    physical attributes, position, and performance data.

    :ivar id: Player identifier (inherited)
    :ivar current_team: Current team information (inherited)
    :ivar date: Award date in YYYY-M format (inherited)
    :ivar country: Nationality information (inherited)
    :ivar name: Player name information (inherited)
    :ivar dates: Important dates (birth, joined club) (inherited)
    :ivar type: Award type - 'POTM' (Player of the Month), 'GOTM' (Goal of the Month), 'SOTM' (Save of the Month) (inherited)
    :ivar shirt_num: Player's shirt number
    :ivar weight: Player weight in kg
    :ivar country_of_birth: Country where player was born
    :ivar position: Playing position
    :ivar preferred_foot: Preferred foot (Left/Right)
    :ivar height: Player height in cm
    """

    shirt_num: int
    weight: int
    country_of_birth: str
    position: str
    preferred_foot: str
    height: int
