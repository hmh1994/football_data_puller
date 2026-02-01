from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class GroundRepository(PulseliveRepository[GroundEntity]):
    """Repository for ground entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, GroundEntity)
