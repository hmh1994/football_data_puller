from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class FixtureRepository(BaseRepository[FixtureEntity, str]):
    """
    Fixture repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, FixtureEntity)

    @BaseRepository.with_db_session
    async def read_by_team_on_season(
        self,
        session: AsyncSession,
        season_id: str,
        home_team_id: str | None = None,
        away_team_id: str | None = None,
    ) -> list[FixtureEntity]:
        """
        Retrieve fixture entities filtered by season and optionally by home and away teams.
        Caution: home and away team IDs should be provided exclusively.
        :param session: Database session.
        :param season_id: The season ID to filter fixtures.
        :param home_team_id: If provided, filters fixtures by the home team ID.
        :param away_team_id: If provided, filters fixtures by the away team ID.
        :return: List of fixture entities sorted by game week.
        """
        assert (
            home_team_id or away_team_id
        ), "Either home_team_id or away_team_id must be provided."
        assert (
            home_team_id is None or away_team_id is None
        ), f"Both home_team_id({home_team_id}) and away_team_id({away_team_id}) cannot be provided."
        stmt = select(self.model).filter(
            FixtureEntity.season_id == season_id,
        )
        if home_team_id:
            stmt = stmt.filter(FixtureEntity.home_team_id == home_team_id)
        if away_team_id:
            stmt = stmt.filter(FixtureEntity.away_team_id == away_team_id)
        result = await session.execute(stmt)
        return sorted(list(result.scalars().all()), key=lambda x: x.game_week)
