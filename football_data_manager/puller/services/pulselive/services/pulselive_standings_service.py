from asyncio import gather

from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.repositories.fixtures.fixture_repository import (
    FixtureRepository,
)
from football_data_manager.common.repositories.grounds.ground_repository import (
    GroundRepository,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)
from football_data_manager.common.repositories.team_stats.team_stat_repository import (
    TeamStatRepository,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.puller.services.pulselive.models.responses.standings.pulselive_standings_table_entry_response import (
    PulseliveStandingsTableEntryResponse,
)
from football_data_manager.puller.services.pulselive.services.pulselive_web_client_service import (
    PulseliveWebClientService,
)


class PulseliveStandingsService:
    """
    Standings service for Pulselive API.
    """

    __fixture_repository: FixtureRepository
    __ground_repository: GroundRepository
    __season_repository: SeasonRepository
    __team_repository: TeamRepository
    __team_stats_repository: TeamStatRepository
    __web_client: PulseliveWebClientService

    target_season_id = [
        "PULSELIVE_SEASON_489",
        "PULSELIVE_SEASON_578",
        "PULSELIVE_SEASON_719",
    ]

    def __init__(
        self,
        db_service: DbService,
        pulselive_service: PulseliveWebClientService,
    ):
        self.__fixture_repository = FixtureRepository(db_service)
        self.__ground_repository = GroundRepository(db_service)
        self.__season_repository = SeasonRepository(db_service)
        self.__team_repository = TeamRepository(db_service)
        self.__team_stats_repository = TeamStatRepository(db_service)
        self.__web_client = pulselive_service

    async def pull_standings(self):
        """
        Pulls standings from the Pulselive API.
        """
        seasons: list[SeasonEntity] = await gather(
            *[
                self.__season_repository.read_by_id(season_id)
                for season_id in self.target_season_id
            ]
        )
        for season in seasons:
            team_stats: list[TeamStatEntity] = await self.__get_team_stats(season)
            await self.__team_stats_repository.create_all(team_stats)

    async def __get_team_stats(self, season: SeasonEntity) -> list[TeamStatEntity]:
        response = await self.__web_client.get_football_standings(
            comp_season_id=int(season.source_id),
            competition_id=season.competition.pulselive_id,
        )
        team_stats: list[TeamStatEntity] = await gather(
            *[
                self.__process_team_stats(season, team_response)
                for team_response in response.tables[0].entries
            ]
        )
        for team_stat in team_stats:
            team_stat.apply_position(team_stats)
        return team_stats

    async def __process_team_stats(
        self, season: SeasonEntity, team_response: PulseliveStandingsTableEntryResponse
    ) -> TeamStatEntity:
        team = await self.__team_repository.read_by_source_id(team_response.team.id)
        team_stat = await self.__team_stats_repository.read_by_source_id(
            TeamStatEntity.get_source_id(season, team)
        )
        if team_stat is not None:
            return team_stat
        else:
            ground = await self.__ground_repository.read_by_source_id(
                team_response.ground.id
            )
            team_stat = TeamStatEntity(ground=ground, season=season, team=team)
            await self.__update_team_stat(season, team, team_stat)
            return team_stat

    async def __update_team_stat(
        self,
        season: SeasonEntity,
        team: TeamEntity,
        team_stat: TeamStatEntity,
    ):
        away_fixtures: list[FixtureEntity] = (
            await self.__fixture_repository.read_by_team_on_season(
                season_id=season.id,
                away_team_id=team.id,
            )
        )
        home_fixtures: list[FixtureEntity] = (
            await self.__fixture_repository.read_by_team_on_season(
                season_id=season.id,
                home_team_id=team.id,
            )
        )
        fixtures = sorted(away_fixtures + home_fixtures, key=lambda f: f.kickoff_time)
        fixtures = filter(
            lambda f: f.id not in team_stat.overall_fixtures and f.clock is not None,
            fixtures,
        )
        for fixture in fixtures:
            team_stat.apply_position(fixture)
