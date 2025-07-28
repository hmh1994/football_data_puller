from football_data_manager.common.new_repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.new_repositories.staffs.staff_entity import (
    StaffEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class StaffRepository(PulseliveRepository[StaffEntity]):
    """ """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, StaffEntity)
