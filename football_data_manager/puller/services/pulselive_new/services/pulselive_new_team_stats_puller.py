from httpx import HTTPStatusError

from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.repositories.fixtures.fixture_repository import (
    FixtureRepository,
)
from football_data_manager.common.repositories.grounds.ground_entity import (
    GroundEntity,
)
from football_data_manager.common.repositories.grounds.ground_repository import (
    GroundRepository,
)
from football_data_manager.common.repositories.matches.match_entity import MatchEntity
from football_data_manager.common.repositories.matches.match_repository import (
    MatchRepository,
)
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)
from football_data_manager.common.repositories.team_stats.team_stat_repository import (
    TeamStatRepository,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.puller.services.pulselive_new.components.pulselive_new_webclient import (
    PulseliveNewWebclient,
)
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_team_stats_response import (
    PulseliveNewTeamStatsResponse,
)


class PulseliveNewTeamStatsPuller:
    """
    Service for pulling team statistics data from PulseLive v2 API and updating existing team stats.

    Handles fetching comprehensive team performance statistics for specific teams, competitions
    and seasons, retrieves stored FULLTIME period matches, and updates team stat entities
    with the latest statistical data from the API.

    :ivar __team_stat_repository: Repository for team stat database operations
    :ivar __match_repository: Repository for match database operations
    :ivar __ground_repository: Repository for ground database operations
    :ivar __webclient: HTTP client for PulseLive API requests
    """

    __fixture_repository: FixtureRepository
    __ground_repository: GroundRepository
    __match_repository: MatchRepository
    __team_stat_repository: TeamStatRepository
    __webclient: PulseliveNewWebclient

    class FixtureAndMatch:
        def __init__(self, fixture: FixtureEntity, match: MatchEntity):
            self.fixture = fixture
            self.match = match

    def __init__(
        self,
        repository_container: CommonRepositoryContainer,
        pulselive_service: PulseliveNewWebclient,
    ):
        """
        Initialize the team stats puller.

        :param repository_container: Container with repository instances
        :param pulselive_service: HTTP client for PulseLive API
        """
        self.__fixture_repository = repository_container.fixture_repository()
        self.__ground_repository = repository_container.ground_repository()
        self.__match_repository = repository_container.match_repository()
        self.__team_stat_repository = repository_container.team_stat_repository()
        self.__webclient = pulselive_service

    async def pull_team_stats(
        self,
        team: TeamEntity,
        competition: CompetitionEntity,
        season: SeasonEntity,
        ground: GroundEntity | None,
    ) -> TeamStatEntity | None:
        """
        Pull team statistics for a specific team, competition and season.

        Retrieves comprehensive team performance statistics from the API,
        finds the corresponding team stat entity, and updates it with the
        latest statistical data. Only processes matches that are in FULLTIME period.

        :param team: Team entity to pull statistics for
        :param competition: Competition entity
        :param season: Season entity
        :param ground: Ground entity of the team on season, or None if not found
        :returns: Updated team stat entity, or None if API call fails or team stat not found
        :raises ValueError: If season doesn't belong to competition
        """
        if competition.id != season.competition_id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        try:
            # Find existing team stat entity
            team_stat = await self.__team_stat_repository.read_by_pulselive_id(
                TeamStatEntity.get_source_id(season, team)
            )
            if team_stat is None:
                team_stat = TeamStatEntity(
                    ground=ground,
                    season=season,
                    team=team,
                )

            # Get FULLTIME matches for this team and season
            fixtures = await self.__fixture_repository.read_by_team_on_season(
                season=season, team=team
            )
            fixtures.sort(key=lambda f: f.kickoff_time)

            # Update team statistics with API data
            for fixture in fixtures:
                await self._update_match_stat(team_stat, fixture)

            # Get team statistics from v2 API
            team_stats_response = await self.__webclient.get_v2_team_stats(
                competition.source_id, season.season_source_id, team.source_id
            )
            self._update_team_stat(team_stat, team_stats_response.stats)

            # Save the updated entity
            await self.__team_stat_repository.update(team_stat)

            return team_stat

        except HTTPStatusError as e:
            print(f"Failed to fetch team stats for team {team.source_id}: {e}")
            return None

    async def _update_match_stat(
        self,
        team_stat: TeamStatEntity,
        fixture: FixtureEntity,
    ) -> TeamStatEntity:
        match = await self.__match_repository.read_by_fixture(fixture)
        if match is None or match.period != PeriodEnum.FULLTIME:
            return team_stat

        await self.__team_stat_repository.append_fixtures(
            team_stat, fixture.kickoff_time, match
        )

        return team_stat

    def _update_team_stat(
        self,
        team_stat: TeamStatEntity,
        stats: PulseliveNewTeamStatsResponse,
    ) -> TeamStatEntity:
        successful_crosses = (
            int(stats.successful_crosses_and_corners)
            if stats.successful_crosses_and_corners is not None
            else 0
        )
        successful_long_passes = (
            int(stats.successful_long_passes)
            if stats.successful_long_passes is not None
            else 0
        )
        team_stat.update_stats(
            attack_corners=(
                int(stats.corners_taken_incl_short_corners)
                if stats.corners_taken_incl_short_corners is not None
                else 0
            ),
            attack_crosses=(
                successful_crosses
                + (
                    int(stats.unsuccessful_crosses_and_corners)
                    if stats.unsuccessful_crosses_and_corners is not None
                    else 0
                )
            ),
            attack_crosses_successful=successful_crosses,
            attack_expected_assists=(
                float(stats.expected_assists)
                if stats.expected_assists is not None
                else 0.0
            ),
            attack_expected_goals=(
                float(stats.expected_goals) if stats.expected_goals is not None else 0.0
            ),
            attack_long_balls=(
                successful_long_passes
                + (
                    int(stats.unsuccessful_long_passes)
                    if stats.unsuccessful_long_passes is not None
                    else 0
                )
            ),
            attack_long_balls_successful=successful_long_passes,
            attack_passes=(
                int(stats.total_passes) if stats.total_passes is not None else 0
            ),
            attack_passes_successful=(
                successful_long_passes
                + (
                    int(stats.successful_short_passes)
                    if stats.successful_short_passes
                    else 0
                )
            ),
            attack_shots_on_target=(
                int(stats.shots_on_target_incl_goals)
                if stats.shots_on_target_incl_goals is not None
                else 0
            ),
            attack_total_shots=(
                int(stats.total_shots) if stats.total_shots is not None else 0
            ),
            attack_touches_in_opposition_box=(
                int(stats.touches_in_opp_box)
                if stats.touches_in_opp_box is not None
                else 0
            ),
            average_possession=(
                float(stats.possession_percentage)
                if stats.possession_percentage is not None
                else 0.0
            ),
            defense_blocks=(
                int(stats.blocked_shots) if stats.blocked_shots is not None else 0
            ),
            defense_clean_sheets=(
                int(stats.clean_sheets) if stats.clean_sheets is not None else 0
            ),
            defense_clearances=(
                int(stats.total_clearances) if stats.total_clearances is not None else 0
            ),
            defense_duels_aerial_total=(
                int(stats.aerial_duels) if stats.aerial_duels is not None else 0
            ),
            defense_duels_aerial_won=(
                int(stats.aerial_duels_won) if stats.aerial_duels_won is not None else 0
            ),
            defense_duels_ground_total=(
                int(stats.ground_duels) if stats.ground_duels is not None else 0
            ),
            defense_duels_ground_won=(
                int(stats.ground_duels_won) if stats.ground_duels_won is not None else 0
            ),
            defense_duels_total=(int(stats.duels) if stats.duels is not None else 0),
            defense_duels_won=(
                int(stats.duels_won) if stats.duels_won is not None else 0
            ),
            defense_interceptions=(
                int(stats.interceptions) if stats.interceptions is not None else 0
            ),
            defense_saves=(
                (
                    int(stats.shots_on_conceded_inside_box)
                    if stats.shots_on_conceded_inside_box is not None
                    else 0
                )
                + (
                    int(stats.shots_on_conceded_outside_box)
                    if stats.shots_on_conceded_outside_box is not None
                    else 0
                )
                - (int(stats.goals_conceded) if stats.goals_conceded is not None else 0)
                + (
                    int(stats.penalties_saved)
                    if stats.penalties_saved is not None
                    else 0
                )
            ),
            defense_saves_penalty=(
                int(stats.penalties_saved) if stats.penalties_saved is not None else 0
            ),
            defense_tackles=(
                int(stats.times_tackled) if stats.times_tackled is not None else 0
            ),
            defense_tackles_successful=(
                int(stats.tackles_won) if stats.tackles_won is not None else 0
            ),
            discipline_fouls=(
                int(stats.total_fouls_conceded) if stats.total_fouls_conceded else 0
            ),
            discipline_red_cards=(
                int(stats.total_red_cards) if stats.total_red_cards is not None else 0
            ),
            discipline_red_cards_direct=(
                int(stats.straight_red_cards)
                if stats.straight_red_cards is not None
                else 0
            ),
            discipline_yellow_cards=(
                int(stats.yellow_cards) if stats.yellow_cards is not None else 0
            ),
        )
        return team_stat
