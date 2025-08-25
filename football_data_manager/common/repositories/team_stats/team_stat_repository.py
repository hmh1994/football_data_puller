from datetime import timedelta

from football_data_manager.common.enums.period_enum import PeriodEnum
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
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)


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
        self,
        team_stat: TeamStatEntity,
        fixture_matches: list[tuple[FixtureEntity, MatchEntity]],
    ) -> TeamStatEntity:
        """
        Append fixtures to the team stat entity based on home/away status.

        Categorizes fixtures as home, away, or overall and creates appropriate
        associations if they don't already exist. Uses efficient set-based
        duplicate checking to avoid performance overhead.

        :param team_stat: The team stat entity to append fixtures to
        :param fixture_matches: List of match entities to append
        :returns: The updated team stat entity with new match associations
        """
        # Load existing associations for duplicate checking
        team_stat = await self.load_items(team_stat)

        # Create efficient lookup sets for existing fixtures
        existing_overall_fixtures = {
            assoc.fixture_id for assoc in team_stat.overall_fixture_associations
        }

        for fixture, match in fixture_matches:
            # Skip if match already exists in overall (covers all cases)
            if match.id in existing_overall_fixtures:
                continue
            if match.period != PeriodEnum.FULLTIME:
                continue

            # Create overall association (always created for every match)
            team_stat.overall_fixture_associations.append(
                TeamStatOverallFixtureAssociation(
                    team_stat=team_stat,
                    fixture=fixture,
                    kickoff_time=fixture.kickoff_time,
                    is_home=fixture.home_team_id == team_stat.team_id,
                )
            )

            # Determine if match is home or away for this team
            if match.home_team_id == team_stat.team_id:
                team_stat.home_fixture_associations.append(
                    TeamStatHomeFixtureAssociation(
                        team_stat=team_stat,
                        fixture=fixture,
                        kickoff_time=fixture.kickoff_time,
                    )
                )
            elif match.away_team_id == team_stat.team_id:
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
                    f"Fixture {match.id} does not belong to team {team_stat.team_id}"
                )

        return team_stat

    async def update_match(
        self,
        team_stat: TeamStatEntity,
        match: MatchEntity,
        previous_match: MatchEntity = None,
    ) -> TeamStatEntity:
        """
        Update team statistics based on match results with support for incremental updates.

        For new matches (not yet processed): Processes match results in chronological order.
        For in-progress matches: Updates only goal statistics incrementally based on score changes.
        For completed matches: Updates all statistics including points, wins/draws/losses.

        Validates chronological order for new matches but allows incremental updates
        for matches already being tracked.

        :param team_stat: The team stat entity to update
        :param match: The match entity with current scores and results
        :param previous_match: Previous state of the match (for incremental updates, optional)
        :returns: The updated team stat entity with match results incorporated
        :raises ValueError: If match fixture is not found, or if new match is processed
                           out of chronological order
        """
        # Load existing associations to check for fixture existence
        team_stat = await self.load_items(team_stat)

        # Find the fixture this match is associated with to determine team role
        kickoff_time = None
        fixture_index = None
        for index, assoc in enumerate(team_stat.overall_fixture_associations):
            if assoc.fixture_id == match.fixture_id:
                kickoff_time = assoc.kickoff_time
                fixture_index = index
                break

        if kickoff_time is None or fixture_index is None:
            raise ValueError(
                f"Match fixture {match.fixture_id} not found in team {team_stat.team_id} statistics"
            )

        is_home = team_stat.check_is_home_match(match)

        # Determine match processing type
        expected_match_count = len(team_stat.overall_cumulative_points)
        is_new_match = fixture_index == expected_match_count
        is_incremental_update = (
            fixture_index + 1 == expected_match_count and previous_match is not None
        )

        if not is_new_match and not is_incremental_update:
            if fixture_index >= expected_match_count:
                # New match out of order
                expected_fixture = team_stat.overall_fixture_associations[
                    expected_match_count
                ]
                raise ValueError(
                    f"Match order validation failed: fixture at index {fixture_index} "
                    f"does not match expected sequence position {expected_match_count}. "
                    f"Expected fixture: {expected_fixture.fixture_id} (kickoff: {expected_fixture.kickoff_time}) "
                    f"but received fixture: {match.fixture_id}"
                )
            else:
                # In-progress update without previous match data
                raise ValueError(
                    f"Incremental update requires previous_match parameter for fixture {match.fixture_id}"
                )
        else:
            # Determine if team is playing at home or away
            if is_home:
                # Current team score
                team_score = match.home_team_score
                previous_team_score = (
                    previous_match.home_team_score if previous_match else 0
                )
                team_score_increment = team_score - previous_team_score
                # Opponent team score
                opponent_score = match.away_team_score
                previous_opponent_score = (
                    previous_match.away_team_score if previous_match else 0
                )
                opponent_score_increment = opponent_score - previous_opponent_score
                # Points earned by the team in this match
                points_earned = match.home_point or 0
                previous_points_earned = (
                    previous_match.home_point if previous_match else 0
                )
                points_earned_increment = points_earned - previous_points_earned
            else:
                # Current team score
                team_score = match.away_team_score
                previous_team_score = (
                    previous_match.away_team_score if previous_match else 0
                )
                team_score_increment = team_score - previous_team_score
                # Opponent team score
                opponent_score = match.home_team_score
                previous_opponent_score = (
                    previous_match.home_team_score if previous_match else 0
                )
                opponent_score_increment = opponent_score - previous_opponent_score
                # Points earned by the team in this match
                points_earned = match.away_point or 0
                previous_points_earned = (
                    previous_match.away_point if previous_match else 0
                )
                points_earned_increment = points_earned - previous_points_earned

            # Calculate if match is complete based on kickoff time + match clock + 10 minutes buffer
            is_match_complete = (
                kickoff_time + timedelta(minutes=match.clock + 10) < create_utc_now()
            )

            team_stat.update_increment(
                is_home,
                team_score_increment,
                opponent_score_increment,
                points_earned_increment,
            )

            if is_match_complete:
                if team_stat.overall_matches > expected_match_count:
                    raise ValueError(
                        f"Match {match.fixture_id} is already processed. "
                        f"Cannot update completed match statistics again."
                    )

                # Calculate final match statistics
                match_won = 1 if team_score > opponent_score else 0
                match_drawn = 1 if team_score == opponent_score else 0
                match_lost = 1 if team_score < opponent_score else 0

                # This was an in-progress match being completed for the first time
                team_stat.append_overall_point(points_earned)
                team_stat.overall_matches += 1
                team_stat.overall_matches_won += match_won
                team_stat.overall_matches_drawn += match_drawn
                team_stat.overall_matches_lost += match_lost
                team_stat.overall_points += points_earned

                if is_home:
                    team_stat.append_home_point(points_earned)
                    team_stat.home_matches += 1
                    team_stat.home_matches_won += match_won
                    team_stat.home_matches_drawn += match_drawn
                    team_stat.home_matches_lost += match_lost
                    team_stat.home_points += points_earned
                else:
                    team_stat.append_away_point(points_earned)
                    team_stat.away_matches += 1
                    team_stat.away_matches_won += match_won
                    team_stat.away_matches_drawn += match_drawn
                    team_stat.away_matches_lost += match_lost
                    team_stat.away_points += points_earned

        return team_stat

    async def rebuild_from_matches(
        self, team_stat: TeamStatEntity, matches: list[MatchEntity]
    ) -> TeamStatEntity:
        """
        Rebuild team statistics from scratch using a list of matches.

        Clears all existing statistics and recalculates them from the provided
        matches in chronological order. Validates that all matches belong to
        fixtures associated with this team.

        :param team_stat: The team stat entity to rebuild
        :param matches: List of match entities to process (should be chronologically ordered)
        :returns: The updated team stat entity with recalculated statistics
        :raises ValueError: If matches are out of order or don't belong to team fixtures
        """
        # Load existing associations to validate matches
        team_stat = await self.load_items(team_stat)

        # Create lookup for valid fixture IDs
        valid_fixture_ids = {
            assoc.fixture_id for assoc in team_stat.overall_fixture_associations
        }

        # Validate all matches belong to this team's fixtures
        invalid_matches = [m for m in matches if m.fixture_id not in valid_fixture_ids]
        if invalid_matches:
            invalid_ids = [m.fixture_id for m in invalid_matches]
            raise ValueError(
                f"Invalid matches found: fixtures {invalid_ids} do not belong to team {team_stat.team_id}"
            )

        # Sort matches by fixture order (based on fixture associations)
        team_stat.overall_fixture_associations.sort(key=lambda a: a.kickoff_time)
        team_stat.home_fixture_associations.sort(key=lambda a: a.kickoff_time)
        team_stat.away_fixture_associations.sort(key=lambda a: a.kickoff_time)
        fixture_order = {
            assoc.fixture_id: idx
            for idx, assoc in enumerate(team_stat.overall_fixture_associations)
        }
        sorted_matches = sorted(
            matches, key=lambda m: fixture_order.get(m.fixture_id, float("inf"))
        )

        # Reset all statistics to initial values
        team_stat.reset_statistics()

        # Process each match in order using the new match logic
        for match in sorted_matches:
            try:
                team_stat = await self.update_match(team_stat, match)
            except Exception as e:
                raise ValueError(
                    f"Failed to process match {match.fixture_id}: {str(e)}"
                ) from e

        return team_stat

    class __TeamStatComparator:
        target: TeamStatEntity
        home: MatchEntity | None
        away: MatchEntity | None

        def __init__(
            self,
            target: TeamStatEntity,
            home: MatchEntity | None = None,
            away: MatchEntity | None = None,
        ) -> None:
            """
            Initialize a comparator for team statistics.

            :param target: The target team stat entity to compare against
            :param home: Optional home match entity for head-to-head comparison
            :param away: Optional away match entity for head-to-head comparison
            """
            self.target = target
            self.home = home
            self.away = away

    async def update_position(
        self,
        target_team_stat: TeamStatEntity,
        other_team_stats: list[TeamStatEntity],
        matches: list[MatchEntity],
    ) -> TeamStatEntity:
        """
        Update team standings positions based on comparison with other teams.

        Calculates overall, home, and away positions by comparing the target team's
        statistics against all other teams in the same season. Uses football ranking
        criteria: points, goal difference, goals scored, and head-to-head results.

        :param target_team_stat: The team stat entity to update positions for
        :param other_team_stats: List of other team stat entities to compare against
        :param matches: List of match entities to consider for head-to-head comparisons
        :returns: The updated team stat entity with refreshed position values
        """
        # Load target team associations for head-to-head comparisons
        target_team_stat = await self.load_items(target_team_stat)

        # Filter to only teams from the same season, excluding the target team
        comparable_teams = {
            team_stat.team_id: self.__TeamStatComparator(team_stat, None, None)
            for team_stat in other_team_stats
            if team_stat.team_id != target_team_stat.team_id
            and team_stat.season_id == target_team_stat.season_id
        }

        for match in matches:
            if target_team_stat.check_is_home_match(match):
                comparable_teams[match.away_team_id].home = match
            elif target_team_stat.check_is_away_match(match):
                comparable_teams[match.home_team_id].away = match
            else:
                raise ValueError(
                    f"Match {match.id} does not belong to target team {target_team_stat.team_id}"
                )

        # Calculate positions by counting teams that rank lower (comparison >= 0)
        overall_comparisons = []
        home_comparisons = []
        away_comparisons = []

        for other_team in comparable_teams.values():
            other_team_stat = await self.load_items(other_team.target)
            overall_comparisons.append(
                target_team_stat.compare_overall(
                    other_team_stat, other_team.home, other_team.away
                )
            )
            home_comparisons.append(target_team_stat.compare_home(other_team_stat))
            away_comparisons.append(target_team_stat.compare_away(other_team_stat))

        # Position = number of teams that rank lower + 1
        target_team_stat.overall_position = (
            sum(comp >= 0 for comp in overall_comparisons) + 1
        )
        target_team_stat.home_position = sum(comp >= 0 for comp in home_comparisons) + 1
        target_team_stat.away_position = sum(comp >= 0 for comp in away_comparisons) + 1

        return target_team_stat
