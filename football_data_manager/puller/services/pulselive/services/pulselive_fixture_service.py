from asyncio import gather
from datetime import datetime

from football_data_manager.common.new_repositories.competitions.competition_repository import (
    CompetitionRepository,
)
from football_data_manager.common.new_repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.new_repositories.fixtures.fixture_repository import (
    FixtureRepository,
)
from football_data_manager.common.new_repositories.grounds.ground_repository import (
    GroundRepository,
)
from football_data_manager.common.new_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.new_repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.new_repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.puller.services.pulselive.models.responses.fixtures.pulselive_fixture_response import (
    PulseliveFixtureResponse,
)
from football_data_manager.puller.services.pulselive.services.pulselive_web_client_service import (
    PulseliveWebClientService,
)


class PulseliveFixturesService:
    """
    Fixtures puller service for Pulselive API.
    """

    __competition_repository: CompetitionRepository
    __fixture_repository: FixtureRepository
    __ground_repository: GroundRepository
    __season_repository: SeasonRepository
    __team_repository: TeamRepository
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
        self.__competition_repository = CompetitionRepository(db_service)
        self.__fixture_repository = FixtureRepository(db_service)
        self.__ground_repository = GroundRepository(db_service)
        self.__season_repository = SeasonRepository(db_service)
        self.__team_repository = TeamRepository(db_service)
        self.__web_client = pulselive_service

    async def pull_fixtures(self):
        """
        Pulls fixtures from the Pulselive API.
        """
        seasons: list[SeasonEntity] = await gather(
            *[
                self.__season_repository.read_by_id(season_id)
                for season_id in self.target_season_id
            ]
        )
        for season in seasons:
            fixtures: list[FixtureEntity] = await self.__get_fixture(season)
            await self.__fixture_repository.create_all(fixtures)

    async def __get_fixture(
        self,
        season: SeasonEntity,
    ) -> list[FixtureEntity]:
        results: list[FixtureEntity] = list()
        page = 0
        while True:
            response = await self.__web_client.get_football_fixtures(
                competition_id=season.competition.pulselive_id,
                comp_season_id=int(season.source_id),
                page=page,
            )
            if len(response) == 0:
                break
            results.extend(
                await gather(
                    *[self.__process_fixture(item, season) for item in response]
                )
            )
            page += 1
        return results

    async def __process_fixture(
        self, response: PulseliveFixtureResponse, season: SeasonEntity
    ) -> FixtureEntity:
        fixture = FixtureRepository.read_by_source_id(response.id)
        if fixture is not None:
            return fixture
        else:
            away_team, ground, home_team, season = await gather(
                self.__team_repository.read_by_source_id(response.teams[1].team.id),
                self.__ground_repository.read_by_source_id(response.ground.id),
                self.__team_repository.read_by_source_id(response.teams[0].team.id),
                self.__season_repository.read_by_source_id(season.id),
            )
            return FixtureEntity(
                away_team=away_team,
                away_team_score=response.teams[1].score,
                attendance=response.attendance,
                clock=response.clock.secs if response.clock is not None else None,
                game_week=response.gameweek.gameweek,
                ground=ground,
                home_team=home_team,
                home_team_score=response.teams[0].score,
                neutral_ground=response.neutral_ground,
                kickoff_time=(
                    datetime.fromtimestamp(response.kickoff.millis / 1000.0)
                    if response.kickoff.completeness
                    else datetime.fromtimestamp(
                        response.provisional_kickoff.millis / 1000.0
                    )
                ),
                season=season,
                source_id=str(response.id),
            )
