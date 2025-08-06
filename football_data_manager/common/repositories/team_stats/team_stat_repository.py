from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.team_stats.team_stat_away_fixture_association import (
    TeamStatAwayFixtureAssociation,
)
from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)
from football_data_manager.common.repositories.team_stats.team_stat_home_fixture_association import (
    TeamStatHomeFixtureAssociation,
)
from football_data_manager.common.repositories.team_stats.team_stat_overall_fixture_association import (
    TeamStatOverallFixtureAssociation,
)
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.common.utils.type_helper.int_helper import compare_ints


class TeamStatRepository(PulseliveRepository[TeamStatEntity]):
    """
    Repository for managing team statistics entities and their fixture associations.

    Provides specialized functionality for handling team performance data including
    home, away, and overall statistics with fixture associations. Extends
    PulseliveRepository to inherit source-specific operations.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, TeamStatEntity)

    async def load_items(self, team_stat: TeamStatEntity) -> TeamStatEntity:
        """
        Load all team stat fixture association items (lazy-loaded relationships).

        Loads all fixture association collections for home, away, and overall
        statistics to enable proper manipulation and analysis.

        :param team_stat: The team stat entity to load items for
        :returns: The team stat entity with all fixture associations loaded
        """
        return await self._load_lazy_fields(
            team_stat,
            [
                TeamStatHomeFixtureAssociation.FIXTURE_COLLECTION_NAME,
                TeamStatAwayFixtureAssociation.FIXTURE_COLLECTION_NAME,
                TeamStatOverallFixtureAssociation.FIXTURE_COLLECTION_NAME,
            ],
        )

    async def read_by_season(self, season: SeasonEntity) -> list[TeamStatEntity]:
        """
        Read team statistics for a specific season.

        Retrieves all team statistics entities associated with the given season,
        providing comprehensive season-wide performance data.

        :param season: Season entity to filter team statistics
        :returns: List of team statistics entities for the specified season
        """
        return await self._read_by_field(season_id=season.id)

    async def append_fixtures(
        self, team_stat: TeamStatEntity, fixtures: list[FixtureEntity]
    ) -> TeamStatEntity:
        """
        Append fixtures to the team stat entity based on home/away status.

        Categorizes fixtures as home, away, or overall and creates appropriate
        associations if they don't already exist. Uses efficient set-based
        duplicate checking to avoid performance overhead.

        :param team_stat: The team stat entity to append fixtures to
        :param fixtures: List of fixture entities to append
        :returns: The updated team stat entity with new fixture associations
        """
        # Load existing associations for duplicate checking
        team_stat = await self.load_items(team_stat)

        # Create efficient lookup sets for existing fixtures
        existing_overall_fixtures = {
            assoc.fixture_id for assoc in team_stat.overall_fixture_associations
        }

        for fixture in fixtures:
            # Skip if fixture already exists in overall (covers all cases)
            if fixture.id in existing_overall_fixtures:
                continue

            # Create overall association (always created for every fixture)
            team_stat.overall_fixture_associations.append(
                TeamStatOverallFixtureAssociation(
                    team_stat=team_stat,
                    fixture=fixture,
                    kickoff_time=fixture.kickoff_time,
                )
            )

            # Determine if fixture is home or away for this team
            if fixture.home_team_id == team_stat.team_id:
                team_stat.home_fixture_associations.append(
                    TeamStatHomeFixtureAssociation(
                        team_stat=team_stat,
                        fixture=fixture,
                        kickoff_time=fixture.kickoff_time,
                    )
                )
            elif fixture.away_team_id == team_stat.team_id:
                team_stat.away_fixture_associations.append(
                    TeamStatAwayFixtureAssociation(
                        team_stat=team_stat,
                        fixture=fixture,
                        kickoff_time=fixture.kickoff_time,
                    )
                )
            else:
                # Fixture doesn't belong to this team - skip or raise error
                raise ValueError(
                    f"Fixture {fixture.id} does not belong to team {team_stat.team_id}"
                )

        return team_stat

    async def update_fixture(
        self, team_stat: TeamStatEntity, fixture: FixtureEntity
    ) -> TeamStatEntity:
        """
        Update an existing fixture in the team stat entity associations.

        Finds existing fixture associations by fixture_id and updates their
        kickoff_time to match the updated fixture. Updates all relevant
        associations (home, away, and overall) where the fixture exists.

        :param team_stat: The team stat entity containing fixture associations
        :param fixture: The updated fixture entity with new information
        :returns: The updated team stat entity with refreshed fixture associations
        """
        # Load existing associations to find the fixture
        team_stat = await self.load_items(team_stat)

        # Update overall fixture associations
        for assoc in team_stat.overall_fixture_associations:
            if assoc.fixture_id == fixture.id:
                assoc.kickoff_time = fixture.kickoff_time
                break

        # Determine if this is a home or away fixture for this team and update accordingly
        if fixture.home_team_id == team_stat.team_id:
            # Update home fixture associations
            for assoc in team_stat.home_fixture_associations:
                if assoc.fixture_id == fixture.id:
                    assoc.kickoff_time = fixture.kickoff_time
                    break
        elif fixture.away_team_id == team_stat.team_id:
            # Update away fixture associations
            for assoc in team_stat.away_fixture_associations:
                if assoc.fixture_id == fixture.id:
                    assoc.kickoff_time = fixture.kickoff_time
                    break
        else:
            # Fixture doesn't belong to this team
            raise ValueError(
                f"Fixture {fixture.id} does not belong to team {team_stat.team_id}"
            )

        return team_stat

    async def update_match(
        self, team_stat: TeamStatEntity, match: MatchEntity
    ) -> TeamStatEntity:
        """
        Update team statistics based on completed match results.

        Processes match results and updates team statistics including goals scored,
        goals conceded, matches played, wins/draws/losses, points, and cumulative points.
        Updates both home/away specific statistics and overall statistics.

        Validates that matches are processed in the correct chronological order
        (by kickoff_time) to maintain data integrity of cumulative statistics.

        :param team_stat: The team stat entity to update
        :param match: The completed match entity with final scores and results
        :returns: The updated team stat entity with match results incorporated
        :raises ValueError: If match fixture is not found, or if match is processed
                           out of chronological order, or if all fixtures have
                           already been processed
        """
        # Load existing associations to check for fixture existence
        team_stat = await self.load_items(team_stat)

        # Find the fixture this match is associated with to determine team role
        fixture_found = None
        fixture_index = None
        for index, assoc in enumerate(team_stat.overall_fixture_associations):
            if assoc.fixture_id == match.fixture_id:
                fixture_found = assoc.fixture
                fixture_index = index
                break

        if not fixture_found:
            raise ValueError(
                f"Match fixture {match.fixture_id} not found in team {team_stat.team_id} statistics"
            )

        # Validate match sequence: ensure this match corresponds to the next expected fixture
        expected_match_count = len(team_stat.overall_cumulative_points)
        total_fixtures = len(team_stat.overall_fixture_associations)

        if expected_match_count >= total_fixtures:
            raise ValueError(
                f"Match sequence validation failed: all fixtures have already been processed. "
                f"Total fixtures: {total_fixtures}, processed matches: {expected_match_count}"
            )

        if fixture_index != expected_match_count:
            expected_fixture = team_stat.overall_fixture_associations[
                expected_match_count
            ]
            raise ValueError(
                f"Match order validation failed: fixture at index {fixture_index} "
                f"does not match expected sequence position {expected_match_count}. "
                f"Expected fixture: {expected_fixture.fixture_id} (kickoff: {expected_fixture.kickoff_time}) "
                f"but received fixture: {match.fixture_id}"
            )

        # Determine if team is playing at home or away
        if fixture_found.home_team_id == team_stat.team_id:
            is_home = True
            team_score = match.home_team_score
            opponent_score = match.away_team_score
            points_earned = match.home_point or 0
        elif fixture_found.away_team_id == team_stat.team_id:
            is_home = False
            team_score = match.away_team_score
            opponent_score = match.home_team_score
            points_earned = match.away_point or 0
        else:
            raise ValueError(
                f"Match fixture {match.fixture_id} does not belong to team {team_stat.team_id}"
            )

        # Calculate match statistics
        goal_difference = team_score - opponent_score
        match_won = 1 if team_score > opponent_score else 0
        match_drawn = 1 if team_score == opponent_score else 0
        match_lost = 1 if team_score < opponent_score else 0

        # Update overall statistics
        self.__append_point(team_stat.overall_cumulative_points, points_earned)
        team_stat.overall_goals_for += team_score
        team_stat.overall_goals_against += opponent_score
        team_stat.overall_goals_difference += goal_difference
        team_stat.overall_matches += 1
        team_stat.overall_matches_won += match_won
        team_stat.overall_matches_drawn += match_drawn
        team_stat.overall_matches_lost += match_lost
        team_stat.overall_points += points_earned

        # Update home/away specific statistics
        if is_home:
            self.__append_point(team_stat.home_cumulative_points, points_earned)
            team_stat.home_goals_for += team_score
            team_stat.home_goals_against += opponent_score
            team_stat.home_goals_difference += goal_difference
            team_stat.home_matches += 1
            team_stat.home_matches_won += match_won
            team_stat.home_matches_drawn += match_drawn
            team_stat.home_matches_lost += match_lost
            team_stat.home_points += points_earned
        else:
            self.__append_point(team_stat.away_cumulative_points, points_earned)
            team_stat.away_goals_for += team_score
            team_stat.away_goals_against += opponent_score
            team_stat.away_goals_difference += goal_difference
            team_stat.away_matches += 1
            team_stat.away_matches_won += match_won
            team_stat.away_matches_drawn += match_drawn
            team_stat.away_matches_lost += match_lost
            team_stat.away_points += points_earned

        return team_stat

    @staticmethod
    def __append_point(points: list[int], point: int):
        """
        Append cumulative points to the points list.

        :param points: List of cumulative points
        :param point: Points to add to the cumulative total
        """
        last_point = points[-1] if points else 0
        points.append(last_point + point)

    async def update_position(
        self, target_team_stat: TeamStatEntity, other_team_stats: list[TeamStatEntity]
    ) -> TeamStatEntity:
        """
        Update team standings positions based on comparison with other teams.

        Calculates overall, home, and away positions by comparing the target team's
        statistics against all other teams in the same season. Uses football ranking
        criteria: points, goal difference, goals scored, and head-to-head results.

        :param target_team_stat: The team stat entity to update positions for
        :param other_team_stats: List of other team stat entities to compare against
        :returns: The updated team stat entity with refreshed position values
        """
        # Load target team associations for head-to-head comparisons
        target_team_stat = await self.load_items(target_team_stat)

        # Filter to only teams from the same season, excluding the target team
        comparable_teams = [
            team_stat
            for team_stat in other_team_stats
            if team_stat.team_id != target_team_stat.team_id
            and team_stat.season_id == target_team_stat.season_id
        ]

        # Calculate positions by counting teams that rank lower (comparison >= 0)
        overall_comparisons = []
        home_comparisons = []
        away_comparisons = []

        for other_team in comparable_teams:
            # Load other team's associations for head-to-head comparison
            other_team = await self.load_items(other_team)

            overall_comparisons.append(
                await self._compare_overall_standing(target_team_stat, other_team)
            )
            home_comparisons.append(
                self._compare_home_standing(target_team_stat, other_team)
            )
            away_comparisons.append(
                self._compare_away_standing(target_team_stat, other_team)
            )

        # Position = number of teams that rank lower + 1
        target_team_stat.overall_position = (
            sum(comp >= 0 for comp in overall_comparisons) + 1
        )
        target_team_stat.home_position = sum(comp >= 0 for comp in home_comparisons) + 1
        target_team_stat.away_position = sum(comp >= 0 for comp in away_comparisons) + 1

        return target_team_stat

    @staticmethod
    async def _compare_overall_standing(
        team_a: TeamStatEntity, team_b: TeamStatEntity
    ) -> int:
        """
        Compare overall standings between two teams using football ranking criteria.

        Ranking order: Points > Goal Difference > Goals Scored > Head-to-head > Away goals

        :param team_a: First team to compare
        :param team_b: Second team to compare
        :returns: 1 if team_a ranks higher, -1 if team_b ranks higher, 0 if equal
        """
        # Compare points
        points_comparison = compare_ints(team_a.overall_points, team_b.overall_points)
        if points_comparison != 0:
            return points_comparison

        # Compare goal difference
        goal_diff_comparison = compare_ints(
            team_a.overall_goals_difference, team_b.overall_goals_difference
        )
        if goal_diff_comparison != 0:
            return goal_diff_comparison

        # Compare goals scored
        goals_scored_comparison = compare_ints(
            team_a.overall_goals_for, team_b.overall_goals_for
        )
        if goals_scored_comparison != 0:
            return goals_scored_comparison

        # Head-to-head comparison
        try:
            # Find head-to-head matches between the two teams
            team_a_home_match = next(
                (
                    assoc
                    for assoc in team_a.home_fixture_associations
                    if assoc.fixture.away_team_id == team_b.team_id
                ),
                None,
            )
            team_a_away_match = next(
                (
                    assoc
                    for assoc in team_a.away_fixture_associations
                    if assoc.fixture.home_team_id == team_b.team_id
                ),
                None,
            )

            if team_a_home_match or team_a_away_match:
                # Calculate head-to-head points
                team_a_h2h_points = 0
                team_b_h2h_points = 0

                if team_a_home_match:
                    team_a_h2h_points += team_a_home_match.fixture.home_point or 0
                    team_b_h2h_points += team_a_home_match.fixture.away_point or 0

                if team_a_away_match:
                    team_a_h2h_points += team_a_away_match.fixture.away_point or 0
                    team_b_h2h_points += team_a_away_match.fixture.home_point or 0

                h2h_points_comparison = compare_ints(
                    team_a_h2h_points, team_b_h2h_points
                )
                if h2h_points_comparison != 0:
                    return h2h_points_comparison

                # If points are equal, compare away goals in head-to-head
                if team_a_home_match and team_a_away_match:
                    team_a_away_goals = team_a_away_match.fixture.away_team_score
                    team_b_away_goals = team_a_home_match.fixture.away_team_score
                    return compare_ints(team_a_away_goals, team_b_away_goals)

        except Exception:
            # If head-to-head comparison fails, continue with other criteria
            pass

        # If all criteria are equal, teams have the same rank
        return 0

    @staticmethod
    def _compare_home_standing(team_a: TeamStatEntity, team_b: TeamStatEntity) -> int:
        """
        Compare home standings between two teams.

        Ranking order: Home Points > Home Goal Difference > Home Goals Scored

        :param team_a: First team to compare
        :param team_b: Second team to compare
        :returns: 1 if team_a ranks higher, -1 if team_b ranks higher, 0 if equal
        """
        # Compare home points
        points_comparison = compare_ints(team_a.home_points, team_b.home_points)
        if points_comparison != 0:
            return points_comparison

        # Compare home goal difference
        goal_diff_comparison = compare_ints(
            team_a.home_goals_difference, team_b.home_goals_difference
        )
        if goal_diff_comparison != 0:
            return goal_diff_comparison

        # Compare home goals scored
        return compare_ints(team_a.home_goals_for, team_b.home_goals_for)

    @staticmethod
    def _compare_away_standing(team_a: TeamStatEntity, team_b: TeamStatEntity) -> int:
        """
        Compare away standings between two teams.

        Ranking order: Away Points > Away Goal Difference > Away Goals Scored

        :param team_a: First team to compare
        :param team_b: Second team to compare
        :returns: 1 if team_a ranks higher, -1 if team_b ranks higher, 0 if equal
        """
        # Compare away points
        points_comparison = compare_ints(team_a.away_points, team_b.away_points)
        if points_comparison != 0:
            return points_comparison

        # Compare away goal difference
        goal_diff_comparison = compare_ints(
            team_a.away_goals_difference, team_b.away_goals_difference
        )
        if goal_diff_comparison != 0:
            return goal_diff_comparison

        # Compare away goals scored
        return compare_ints(team_a.away_goals_for, team_b.away_goals_for)
