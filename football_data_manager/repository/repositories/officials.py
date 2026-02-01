from football_data_manager.repository.entities.officials import OfficialEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class OfficialRepository(PulseliveRepository[OfficialEntity]):
    """Repository for official entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, OfficialEntity)
