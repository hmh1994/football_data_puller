from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class CompetitionRepository(PulseliveRepository[CompetitionEntity]):
    """Repository for competition entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, CompetitionEntity)
