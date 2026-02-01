from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class FixtureRepository(PulseliveRepository[FixtureEntity]):
    """Repository for fixture entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, FixtureEntity)
