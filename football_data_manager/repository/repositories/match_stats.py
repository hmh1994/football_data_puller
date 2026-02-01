from football_data_manager.repository.entities.match_stats import MatchStatEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class MatchStatRepository(PulseliveRepository[MatchStatEntity]):
    """Repository for match stat entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, MatchStatEntity)
