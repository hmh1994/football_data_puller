from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.new_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.new_repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.db.db_service import DbService


class FixtureRepository(BaseRepository[FixtureEntity]):
    """
    Fixture repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, FixtureEntity)

    @BaseRepository.with_db_session
    async def read_by_team_on_season(
        self, session: AsyncSession, season: SeasonEntity, team: TeamEntity
    ) -> list[FixtureEntity]:
        """
        Reads fixtures for a specific team in a given season.
        :param session: Database session.
        :param season: Season entity to filter fixtures.
        :param team: Team entity to filter fixtures.
        :return: List of fixture entities sorted by game week.
        """
        stmt = select(self.model).filter(
            self.model.season_id == season.id,
            or_(
                self.model.home_team_id == team.id,
                self.model.away_team_id == team.id,
            ),
        )
        result = await session.execute(stmt)
        return sorted(list(result.scalars().all()), key=lambda x: x.game_week)
