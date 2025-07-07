from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.new_repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class TeamStatRepository(BaseRepository[TeamStatEntity]):
    """
    Team statistics repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, TeamStatEntity)

    @BaseRepository.with_db_session
    async def read_by_season(
        self, session: AsyncSession, season: SeasonEntity
    ) -> list[TeamStatEntity]:
        """
        Reads team statistics for a specific season.
        :param session: Database session.
        :param season: Season entity to filter team statistics.
        :return: List of team statistics entities for the specified season.
        """
        stmt = select(self.model).filter_by(season_id=season.id)
        result = await session.execute(stmt)
        return list(result.unique().scalars().all())
