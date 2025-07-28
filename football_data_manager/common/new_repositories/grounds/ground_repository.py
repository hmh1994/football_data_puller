from football_data_manager.common.new_repositories.grounds.ground_entity import (
    GroundEntity,
)
from football_data_manager.common.new_repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class GroundRepository(PulseliveRepository[GroundEntity]):
    """
    Ground repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, GroundEntity)
