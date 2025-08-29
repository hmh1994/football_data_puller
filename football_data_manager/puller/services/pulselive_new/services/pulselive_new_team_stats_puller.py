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
from football_data_manager.puller.services.pulselive_new.models.responses.pulselive_new_v2_team_stats_response import (
    PulseliveNewV2TeamStatsResponse,
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
        :returns: Updated team stat entity, or None if API call fails or team stat not found
        :raises ValueError: If season doesn't belong to competition
        """
        if competition.id != season.competition_id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        try:
            # Get team statistics from v2 API
            team_stats_response = await self.__webclient.get_v2_team_stats(
                competition.source_id, season.season_source_id, team.source_id
            )

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
            updated_team_stat = await self._update_team_stat_with_api_data(
                team_stat, team_stats_response, fixtures
            )

            # Save the updated entity
            await self.__team_stat_repository.update(updated_team_stat)

            return updated_team_stat

        except HTTPStatusError as e:
            print(f"Failed to fetch team stats for team {team.source_id}: {e}")
            return None

    async def _update_team_stat_with_api_data(
        self,
        team_stat: TeamStatEntity,
        team_stats_response: PulseliveNewV2TeamStatsResponse,
        fixtures: list[FixtureEntity],
    ) -> TeamStatEntity:
        stats = team_stats_response.stats

        matches = []
        for fixture in fixtures:
            match = await self.__match_repository.read_by_fixture(fixture)
            if match is not None and match.period == PeriodEnum.FULLTIME:
                matches.append(self.FixtureAndMatch(fixture, match))

        match_fixtures = []
        for match in fulltime_matches:
            fixture = await self.__fixture_repository.read_by_id(match.match_id)
            match_fixtures.append((fixture, match))
        match_fixtures.sort(key=lambda x: x[0].kickoff_time)

        await self.__team_stat_repository.append_fixtures(team_stat, match_fixtures)
        for idx in range(len(match_fixtures) - 1):
            team_stat = await self.__team_stat_repository.update_match(
                team_stat,
                match_fixtures[idx][1],
                match_fixtures[idx - 1][1] if idx > 0 else None,
            )

        # Update attack statistics
        if stats.corners_taken_incl_short_corners is not None:
            team_stat.overall_stat_attack_corners = int(
                stats.corners_taken_incl_short_corners
            )

        if stats.total_passes is not None:
            team_stat.overall_stat_attack_passes = int(stats.total_passes)

        if (
            stats.successful_short_passes is not None
            and stats.successful_long_passes is not None
        ):
            team_stat.overall_stat_attack_passes_successful = int(
                stats.successful_short_passes + stats.successful_long_passes
            )

        if (
            stats.successful_long_passes is not None
            and stats.unsuccessful_long_passes is not None
        ):
            team_stat.overall_stat_attack_long_balls = int(
                stats.successful_long_passes + stats.unsuccessful_long_passes
            )
            team_stat.overall_stat_attack_long_balls_successful = int(
                stats.successful_long_passes
            )

        if (
            stats.successful_crosses_and_corners is not None
            and stats.unsuccessful_crosses_and_corners is not None
        ):
            team_stat.overall_stat_attack_crosses = int(
                stats.successful_crosses_and_corners
                + stats.unsuccessful_crosses_and_corners
            )
            team_stat.overall_stat_attack_crosses_successful = int(
                stats.successful_crosses_and_corners
            )

        if stats.shots_on_target_incl_goals is not None:
            team_stat.overall_stat_attack_shots_on_target = int(
                stats.shots_on_target_incl_goals
            )

        if stats.touches_in_opp_box is not None:
            team_stat.overall_stat_attack_touches_in_opposition_box = int(
                stats.touches_in_opp_box
            )

        if stats.expected_goals is not None:
            team_stat.overall_stat_attack_expected_goals = float(stats.expected_goals)

        # Update possession statistics
        if stats.possession_percentage is not None:
            team_stat.overall_stat_average_possession = float(
                stats.possession_percentage
            )

        # Update defense statistics
        if stats.blocked_shots is not None:
            team_stat.overall_stat_defense_blocks = int(stats.blocked_shots)

        if stats.total_clearances is not None:
            team_stat.overall_stat_defense_clearances = int(stats.total_clearances)

        if stats.aerial_duels is not None:
            team_stat.overall_stat_defense_duels_aerial_total = int(stats.aerial_duels)

        if stats.aerial_duels_won is not None:
            team_stat.overall_stat_defense_duels_aerial_won = int(
                stats.aerial_duels_won
            )

        if stats.ground_duels is not None:
            team_stat.overall_stat_defense_duels_ground_total = int(stats.ground_duels)

        if stats.ground_duels_won is not None:
            team_stat.overall_stat_defense_duels_ground_won = int(
                stats.ground_duels_won
            )

        if stats.duels is not None:
            team_stat.overall_stat_defense_duels_total = int(stats.duels)

        if stats.duels_won is not None:
            team_stat.overall_stat_defense_duels_won = int(stats.duels_won)

        if stats.interceptions is not None:
            team_stat.overall_stat_defense_interceptions = int(stats.interceptions)

        if stats.times_tackled is not None:
            team_stat.overall_stat_defense_tackles = int(stats.times_tackled)

        if stats.tackles_won is not None:
            team_stat.overall_stat_defense_tackles_successful = int(stats.tackles_won)

        # Calculate saves (shots on target conceded - goals conceded + penalties saved)
        if (
            stats.shots_on_conceded_inside_box is not None
            and stats.shots_on_conceded_outside_box is not None
            and stats.goals_conceded is not None
        ):
            total_shots_on_target_conceded = (
                stats.shots_on_conceded_inside_box + stats.shots_on_conceded_outside_box
            )
            saves = int(total_shots_on_target_conceded - stats.goals_conceded)
            if stats.penalties_saved is not None:
                saves += int(stats.penalties_saved)
            team_stat.overall_stat_defense_saves = max(0, saves)

        if stats.penalties_saved is not None:
            team_stat.overall_stat_defense_saves_penalty = int(stats.penalties_saved)

        # Update discipline statistics
        if stats.total_fouls_conceded is not None:
            team_stat.overall_stat_discipline_fouls = int(stats.total_fouls_conceded)

        if stats.total_red_cards is not None:
            team_stat.overall_stat_discipline_red_cards = int(stats.total_red_cards)

        if stats.straight_red_cards is not None:
            team_stat.overall_stat_discipline_red_cards_direct = int(
                stats.straight_red_cards
            )

        if stats.yellow_cards is not None:
            team_stat.overall_stat_discipline_yellow_cards = int(stats.yellow_cards)

        return team_stat

    async def _get_ground_for_team(
        self,
        team: TeamEntity,
        competition: CompetitionEntity,
        season: SeasonEntity,
    ) -> GroundEntity | None:
        """
        Get ground entity for a team by calling get_v1_teams API.

        Retrieves team information from v1 teams API to find the associated stadium
        information and returns the corresponding ground entity from the database.

        :param team: Team entity to get ground information for
        :param competition: Competition entity
        :param season: Season entity
        :returns: Ground entity associated with the team, or None if not found
        """
        try:
            # Get teams from v1 API to find stadium information
            teams_response = await self.__webclient.get_v1_teams(
                competition.source_id, season.season_source_id, limit=50
            )

            # Find the team with matching abbreviation
            team_data = None
            for team_item in teams_response.data:
                if team_item.id == team.source_id:
                    team_data = team_item
                    break

            if team_data is None:
                print(
                    f"Team with abbreviation {team.abbreviation} not found in v1 teams API"
                )
                return None

            if team_data.stadium.name is None:
                print(f"No stadium name found for team {team.abbreviation}")
                return None

            # Try to find existing ground by name
            ground = await self.__ground_repository.read_by_name_en(
                team_data.stadium.name
            )

            if ground is None:
                print(
                    f"Ground with name '{team_data.stadium.name}' not found in database"
                )
                return None

            return ground

        except HTTPStatusError as e:
            print(f"Failed to fetch v1 teams for ground lookup: {e}")
            return None
        except Exception as e:
            print(f"Error getting ground for team {team.abbreviation}: {e}")
            return None
