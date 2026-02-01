from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.db.db_service import DbService


class FixtureRepository(PulseliveRepository[FixtureEntity]):
    """
    Repository for managing fixture entities.
    
    Provides specialized functionality for handling football fixtures (matches)
    with team filtering and season-based queries. Extends PulseliveRepository to inherit source-specific operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the fixture repository.
        
        :param db_service: Database service for database operations
        """
        super().__init__(db_service, FixtureEntity)

    @BaseRepository.with_db_session
    async def read_by_team_on_season(
        self, session: AsyncSession, season: SeasonEntity, team: TeamEntity
    ) -> list[FixtureEntity]:
        """
        Read fixtures for a specific team in a given season.

        Retrieves all fixtures where the specified team is either home or away team
        within the given season, sorted by game week for chronological ordering.

        :param session: Database session for the query
        :param season: Season entity to filter fixtures
        :param team: Team entity to filter fixtures (home or away)
        :returns: List of fixture entities sorted by game week
        """
        stmt = select(self.model).filter(
            self.model.season_id == season.id,
            or_(
                self.model.home_team_id == team.id,
                self.model.away_team_id == team.id,
            ),
        )
        result = await session.execute(stmt)
        return sorted(list(result.unique().scalars().all()), key=lambda x: x.game_week)

    @BaseRepository.with_db_session
    async def read_by_season(
        self, session: AsyncSession, season: SeasonEntity
    ) -> list[FixtureEntity]:
        """
        Read all fixtures for a given season.

        Retrieves all fixtures within the specified season, sorted by game week
        for chronological ordering.

        :param session: Database session for the query
        :param season: Season entity to filter fixtures
        :returns: List of fixture entities sorted by game week
        """
        stmt = select(self.model).filter(self.model.season_id == season.id)
        result = await session.execute(stmt)
        return sorted(list(result.unique().scalars().all()), key=lambda x: x.game_week)
