from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class SeasonRepository(PulseliveRepository[SeasonEntity]):
    """Repository for season entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, SeasonEntity)
