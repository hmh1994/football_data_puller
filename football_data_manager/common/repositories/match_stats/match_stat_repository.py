from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.matches.match_entity import MatchEntity
from football_data_manager.common.repositories.match_stats.match_stat_entity import (
    MatchStatEntity,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class MatchStatRepository(PulseliveRepository[MatchStatEntity]):
    """
    Repository for managing match stat entities.

    Provides specialized functionality for handling comprehensive match statistics
    including team performance metrics, analytical queries, and statistical aggregations.
    Extends PulseliveRepository to inherit source-specific operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the match stat repository.

        :param db_service: Database service for database operations
        """
        super().__init__(db_service, MatchStatEntity)

    @BaseRepository.with_db_session
    async def read_by_match(
        self,
        session: AsyncSession,
        match: MatchEntity,
    ) -> list[MatchStatEntity]:
        """
        Read all match stat entities for a given match.

        Retrieves statistics for both home and away teams in the specified match.

        :param session: Database session
        :param match: Match entity to get statistics for
        :returns: List of match stat entities for the match
        """
        stmt = select(MatchStatEntity).where(MatchStatEntity.match_id == match.id)
        result = await session.execute(stmt)
        return list(result.scalars().all())
