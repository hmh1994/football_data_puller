from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class FixtureRepository(PulseliveRepository[FixtureEntity]):
    """Repository for fixture entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, FixtureEntity)

    async def get_by_team_on_season(
        self,
        season: SeasonEntity,
        team: TeamEntity,
        session: AsyncSession | None = None,
    ) -> list[FixtureEntity]:
        """Get fixtures for one team in one season ordered by kickoff."""

        async def _do(s: AsyncSession) -> list[FixtureEntity]:
            stmt = (
                select(FixtureEntity)
                .where(FixtureEntity.season_id == season.id)
                .where(
                    or_(
                        FixtureEntity.home_team_id == team.id,
                        FixtureEntity.away_team_id == team.id,
                    )
                )
                .order_by(FixtureEntity.kickoff_time)
            )
            result = await s.execute(stmt)
            return list(result.scalars().all())

        if session:
            return await _do(session)
        return await self._execute_with_retry(_do)
