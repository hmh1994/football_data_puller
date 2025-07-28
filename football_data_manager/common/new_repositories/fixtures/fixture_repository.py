from asyncio import gather

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.new_repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.new_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.new_repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.db.db_service import DbService


class FixtureRepository(PulseliveRepository[FixtureEntity]):
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
        return sorted(list(result.unique().scalars().all()), key=lambda x: x.game_week)

    @BaseRepository.with_db_session
    async def upsert(
        self, session: AsyncSession, fixture: FixtureEntity
    ) -> FixtureEntity:
        """
        Upserts a fixture entity into the database.
        If a fixture with the same source and source_id exists, it updates the existing fixture.
        :param session: Database session (not used in this method).
        :param fixture: Fixture entity to upsert.
        :return: The upserted fixture entity.
        """
        if old_fixture := await self.read_by_source_id(
            session, fixture.source, fixture.source_id
        ):
            if fixture.clock is None or old_fixture.clock is not None:
                return old_fixture
            else:
                old_fixture.refresh(fixture)
                return await self.update(session, old_fixture)
        else:
            return await self.create(session, fixture)

    async def upsert_all(self, fixtures: list[FixtureEntity]) -> list[FixtureEntity]:
        """
        Upserts multiple fixture entities into the database.
        :param fixtures: List of fixture entities to upsert.
        :return: List of upserted fixture entities.
        """
        return await gather(*[self.upsert(fixture) for fixture in fixtures])
