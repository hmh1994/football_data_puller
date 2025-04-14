from asyncio import gather
from itertools import accumulate

from football_data_manager.common.repositories.fixtures.fixture_repository import (
    FixtureRepository,
)
from football_data_manager.common.repositories.grounds.ground_entity import GroundEntity
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
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
    __season_repository: SeasonRepository
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
        self.__season_repository = SeasonRepository(db_service)
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
            if len(team_stats) == 0:
                continue
            await self.__team_stats_repository.create_all(
                team_stats,
                primary_key=lambda x: x.id,
            )

    async def __get_team_stats(self, season: SeasonEntity) -> list[TeamStatEntity]:
        response = await self.__web_client.get_football_standings(
            comp_season_id=season.pulselive_id,
            competition_id=season.competition.pulselive_id,
        )
        team_stats: list[TeamStatEntity] = await gather(
            *[
                self.__process_team_stats(season, team_response)
                for team_response in response.tables[0].entries
            ]
        )
        for team_stat in team_stats:
            away_position = 1
            home_position = 1
            for other_team in team_stats:
                if team_stat.id == other_team.id:
                    continue

                if team_stat.away_points < other_team.away_points:
                    away_position += 1
                elif team_stat.away_points == other_team.away_points:
                    if (
                        team_stat.away_goals_difference
                        < other_team.away_goals_difference
                    ):
                        away_position += 1
                    elif (
                        team_stat.away_goals_difference
                        == other_team.away_goals_difference
                    ):
                        if team_stat.away_goals_for < other_team.away_goals_for:
                            away_position += 1

                if team_stat.home_points < other_team.home_points:
                    home_position += 1
                elif team_stat.home_points == other_team.home_points:
                    if (
                        team_stat.home_goals_difference
                        < other_team.home_goals_difference
                    ):
                        home_position += 1
                    elif (
                        team_stat.home_goals_difference
                        == other_team.home_goals_difference
                    ):
                        if team_stat.home_goals_for < other_team.home_goals_for:
                            home_position += 1
                team_stat.away_positions = away_position
                team_stat.home_positions = home_position
        return team_stats

    async def __process_team_stats(
        self, season: SeasonEntity, team_response: PulseliveStandingsTableEntryResponse
    ) -> TeamStatEntity:
        team_id = TeamEntity.get_id(team_response.team.id)
        away_fixtures = await self.__fixture_repository.read_by_team_on_season(
            season_id=season.id,
            away_team_id=team_id,
        )
        away_cumulative_points = list(
            accumulate(
                filter(
                    lambda x: x is not None,
                    [fixture.away_point for fixture in away_fixtures],
                ),
            )
        )
        home_fixtures = await self.__fixture_repository.read_by_team_on_season(
            season_id=season.id,
            home_team_id=team_id,
        )
        home_cumulative_points = list(
            accumulate(
                filter(
                    lambda x: x is not None,
                    [fixture.home_point for fixture in home_fixtures],
                ),
            )
        )
        overall_fixtures_with_point = sorted(
            [(fixture.away_point, fixture) for fixture in away_fixtures]
            + [(fixture.home_point, fixture) for fixture in home_fixtures],
            key=lambda x: x[1].game_week,
        )
        overall_cumulative_points = list(
            accumulate(
                filter(
                    lambda x: x is not None,
                    [point for point, _ in overall_fixtures_with_point],
                ),
            )
        )
        return TeamStatEntity(
            id=TeamStatEntity.get_id(f"{season.pulselive_id}_{team_response.team.id}"),
            away_cumulative_points=away_cumulative_points,
            away_fixtures=[fixture.id for fixture in away_fixtures],
            away_goals_against=team_response.away.goals_against,
            away_goals_for=team_response.away.goals_for,
            away_matches=team_response.away.played,
            away_matches_drawn=team_response.away.drawn,
            away_matches_lost=team_response.away.lost,
            away_matches_won=team_response.away.won,
            away_goals_difference=team_response.away.goals_difference,
            away_points=team_response.away.points,
            ground_id=GroundEntity.get_id(team_response.ground.id),
            home_cumulative_points=home_cumulative_points,
            home_fixtures=[fixture.id for fixture in home_fixtures],
            home_matches=team_response.home.played,
            home_matches_drawn=team_response.home.drawn,
            home_matches_lost=team_response.home.lost,
            home_matches_won=team_response.home.won,
            home_goals_against=team_response.home.goals_against,
            home_goals_for=team_response.home.goals_for,
            home_goals_difference=team_response.home.goals_difference,
            home_points=team_response.home.points,
            overall_cumulative_points=overall_cumulative_points,
            overall_fixtures=[fixture.id for _, fixture in overall_fixtures_with_point],
            overall_goals_against=team_response.overall.goals_against,
            overall_goals_for=team_response.overall.goals_for,
            overall_goals_difference=team_response.overall.goals_difference,
            overall_matches=team_response.overall.played,
            overall_matches_drawn=team_response.overall.drawn,
            overall_matches_lost=team_response.overall.lost,
            overall_matches_won=team_response.overall.won,
            overall_points=team_response.overall.points,
            overall_position=team_response.position,
            season_id=season.id,
            team_id=team_id,
        )
