from football_data_manager.repository.entities.staffs import StaffEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class StaffRepository(PulseliveRepository[StaffEntity]):
    """Repository for staff entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, StaffEntity)
