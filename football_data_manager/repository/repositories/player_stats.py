from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class PlayerStatRepository(PulseliveRepository[PlayerStatEntity]):
    """Repository for player stat entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, PlayerStatEntity)
