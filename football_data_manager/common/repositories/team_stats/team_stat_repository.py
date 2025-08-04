from sqlalchemy import select
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
from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class TeamStatRepository(PulseliveRepository[TeamStatEntity]):
    """
    Team statistics repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, TeamStatEntity)

    async def load_fixtures(self, team_stat: TeamStatEntity) -> TeamStatEntity:
        """
        Load fixtures for the given team stat entity.
        This method uses lazy loading to fetch the fixtures associated with the team stat entity.
        :param team_stat: The team stat entity to load fixtures for.
        :return: The team stat entity with fixtures loaded.
        """
        return await self._load_lazy_fields(
            team_stat, ["away_fixtures", "home_fixtures", "overall_fixtures"]
        )

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

    async def update_position(
        self, team_stats: list[TeamStatEntity]
    ) -> list[TeamStatEntity]:
        """
        Update the positions of the team statistics.
        This method processes each team stat entity to determine its position based on the provided list of team stats.
        :param team_stats: List of team stat entities to update positions for.
        :return: List of team stat entities with updated positions.
        """
        new_team_stats = []
        for idx, entity in enumerate(team_stats):
            new_team_stats.append(
                await self.__process_position(
                    entity, team_stats[:idx] + team_stats[idx + 1 :]
                )
            )
        return new_team_stats

    async def append_fixture(
        self, team_stat: TeamStatEntity, fixture: FixtureEntity
    ) -> TeamStatEntity:
        """
        Append a fixture to the team statistics.
        This method checks if the fixture already exists in the team statistics and processes it accordingly.
        :param team_stat: The team stat entity to append the fixture to.
        :param fixture: The fixture entity to append.
        :return: The updated team stat entity with the fixture appended if it did not already exist.
        """
        if fixture.clock is None:
            return team_stat
        merged_team_stat = await self.load_fixtures(team_stat)
        fixture_id_list = [f.id for f in merged_team_stat.overall_fixtures]
        if fixture.id in fixture_id_list:
            return team_stat
        elif any(
            done_fixture.kickoff_time > fixture.kickoff_time
            for done_fixture in merged_team_stat.overall_fixtures
        ):
            overall_fixtures = sorted(
                merged_team_stat.overall_fixtures + [fixture],
                key=lambda f: f.kickoff_time,
            )
            merged_team_stat.initialize()
            for fixture in overall_fixtures:
                merged_team_stat = await self.__process_fixture(
                    merged_team_stat, fixture
                )
            return merged_team_stat
        else:
            return await self.__process_fixture(merged_team_stat, fixture)

    async def __process_fixture(
        self, team_stat: TeamStatEntity, fixture: FixtureEntity
    ) -> TeamStatEntity:
        pass

    async def __process_position(
        self, target: TeamStatEntity, others: list[TeamStatEntity]
    ) -> TeamStatEntity:
        other_overall_metrics, other_home_metrics, other_away_metrics = [], [], []
        pass
