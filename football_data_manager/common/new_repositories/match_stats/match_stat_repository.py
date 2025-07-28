from football_data_manager.common.new_repositories.match_stats.match_stat_entity import (
    MatchStatEntity,
)
from football_data_manager.common.new_repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class MatchStatRepository(PulseliveRepository[MatchStatEntity]):
    """ """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, MatchStatEntity)
