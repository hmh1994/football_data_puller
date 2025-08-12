from typing import Self

from sqlalchemy import Column, String, ForeignKey, Integer, ARRAY

from football_data_manager.common.repositories.constants import (
    TEAM_STATS_TABLE_NAME,
)
from football_data_manager.common.repositories.grounds.ground_entity import (
    GroundEntity,
)
from football_data_manager.common.repositories.matches.match_entity import MatchEntity
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.staffs.staff_entity import StaffEntity
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.utils.type_helper.int_helper import compare_ints


class TeamStatEntity(PulseliveEntity):
    """
    Team statistics entity model with comprehensive match performance data.

    Represents detailed team performance statistics including home, away, and overall
    metrics with fixture associations. Extends PulseliveEntity to inherit source tracking.

    :ivar id: Unique identifier for the team stat
    :ivar away_cumulative_points: Cumulative points progression in away matches
    :ivar away_fixture_associations: List of away fixture associations
    :ivar away_goals_against: Goals conceded in away matches
    :ivar away_goals_for: Goals scored in away matches
    :ivar away_goals_difference: Goal difference in away matches
    :ivar away_matches: Total away matches played
    :ivar away_matches_drawn: Away matches drawn
    :ivar away_matches_lost: Away matches lost
    :ivar away_matches_won: Away matches won
    :ivar away_points: Total points from away matches
    :ivar away_position: Away standings position
    :ivar ground_id: Foreign key to home ground entity
    :ivar home_cumulative_points: Cumulative points progression in home matches
    :ivar home_fixture_associations: List of home fixture associations
    :ivar home_goals_against: Goals conceded in home matches
    :ivar home_goals_for: Goals scored in home matches
    :ivar home_goals_difference: Goal difference in home matches
    :ivar home_matches: Total home matches played
    :ivar home_matches_drawn: Home matches drawn
    :ivar home_matches_lost: Home matches lost
    :ivar home_matches_won: Home matches won
    :ivar home_points: Total points from home matches
    :ivar home_position: Home standings position
    :ivar manager_id: Foreign key to team manager entity (optional)
    :ivar overall_cumulative_points: Cumulative points progression in all matches
    :ivar overall_fixture_associations: List of all fixture associations
    :ivar overall_matches: Total matches played
    :ivar overall_matches_drawn: Total matches drawn
    :ivar overall_matches_lost: Total matches lost
    :ivar overall_matches_won: Total matches won
    :ivar overall_goals_against: Total goals conceded
    :ivar overall_goals_for: Total goals scored
    :ivar overall_goals_difference: Overall goal difference
    :ivar overall_points: Total points from all matches
    :ivar overall_position: Overall standings position
    :ivar season_id: Foreign key to season entity
    :ivar team_id: Foreign key to team entity
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = TEAM_STATS_TABLE_NAME

    away_cumulative_points = Column(ARRAY(Integer), nullable=False)
    away_goals_against = Column(Integer, nullable=False)
    away_goals_for = Column(Integer, nullable=False)
    away_goals_difference = Column(Integer, nullable=False)
    away_matches = Column(Integer, nullable=False)
    away_matches_drawn = Column(Integer, nullable=False)
    away_matches_lost = Column(Integer, nullable=False)
    away_matches_won = Column(Integer, nullable=False)
    away_points = Column(Integer, nullable=False)
    away_position = Column(Integer, nullable=True)
    ground_id = Column(
        String,
        ForeignKey(GroundEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    home_cumulative_points = Column(ARRAY(Integer), nullable=False)
    home_goals_against = Column(Integer, nullable=False)
    home_goals_for = Column(Integer, nullable=False)
    home_goals_difference = Column(Integer, nullable=False)
    home_matches = Column(Integer, nullable=False)
    home_matches_drawn = Column(Integer, nullable=False)
    home_matches_lost = Column(Integer, nullable=False)
    home_matches_won = Column(Integer, nullable=False)
    home_points = Column(Integer, nullable=False)
    home_position = Column(Integer, nullable=True)
    manager_id = Column(String, ForeignKey(StaffEntity.id), nullable=True)
    overall_cumulative_points = Column(ARRAY(Integer), nullable=False)
    overall_goals_against = Column(Integer, nullable=False)
    overall_goals_for = Column(Integer, nullable=False)
    overall_goals_difference = Column(Integer, nullable=False)
    overall_matches = Column(Integer, nullable=False)
    overall_matches_drawn = Column(Integer, nullable=False)
    overall_matches_lost = Column(Integer, nullable=False)
    overall_matches_won = Column(Integer, nullable=False)
    overall_points = Column(Integer, nullable=False)
    overall_position = Column(Integer, nullable=False)
    season_id = Column(
        String,
        ForeignKey(SeasonEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    team_id = Column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )

    def __init__(
        self,
        ground: GroundEntity,
        season: SeasonEntity,
        team: TeamEntity,
    ):
        """
        Initialize a new team stat entity.

        :param ground: Home ground entity associated with the team
        :param season: Season entity for which statistics are recorded
        :param team: Team entity associated with the statistics
        """
        super().__init__(source_id=self.get_source_id(season, team))
        self.away_fixture_associations = []
        self.ground_id = ground.id
        self.home_fixture_associations = []
        self.overall_fixture_associations = []
        self.season_id = season.id
        self.team_id = team.id
        self.reset_statistics()

    @staticmethod
    def get_source_id(season: SeasonEntity, team: TeamEntity) -> str:
        """
        Generate a unique source ID for the team stat entity.

        :param season: Season entity for which statistics are recorded
        :param team: Team entity associated with the statistics
        :returns: Unique source ID combining season and team identifiers
        """
        return f"{season.source_id}_{team.source_id}"

    def check_is_home_match(self, match: MatchEntity) -> bool:
        """
        Check if the match is a home match for this team.

        :param match: Match entity to check
        :returns: True if the match is a home match, False otherwise
        """
        return match.home_team_id == self.team_id

    def check_is_away_match(self, match: MatchEntity) -> bool:
        """
        Check if the match is an away match for this team.

        :param match: Match entity to check
        :returns: True if the match is an away match, False otherwise
        """
        return match.away_team_id == self.team_id

    def reset_statistics(self):
        """
        Reset all team statistics to initial values.

        Resets goals, points, matches played, and win/draw/loss counts for
        overall, home, and away statistics. Preserves fixture associations.
        """
        # Reset overall statistics
        self.overall_cumulative_points = []
        self.overall_goals_for = 0
        self.overall_goals_against = 0
        self.overall_goals_difference = 0
        self.overall_matches = 0
        self.overall_matches_won = 0
        self.overall_matches_drawn = 0
        self.overall_matches_lost = 0
        self.overall_points = 0

        # Reset home statistics
        self.home_cumulative_points = []
        self.home_goals_for = 0
        self.home_goals_against = 0
        self.home_goals_difference = 0
        self.home_matches = 0
        self.home_matches_won = 0
        self.home_matches_drawn = 0
        self.home_matches_lost = 0
        self.home_points = 0

        # Reset away statistics
        self.away_cumulative_points = []
        self.away_goals_for = 0
        self.away_goals_against = 0
        self.away_goals_difference = 0
        self.away_matches = 0
        self.away_matches_won = 0
        self.away_matches_drawn = 0
        self.away_matches_lost = 0
        self.away_points = 0

    def update_increment(
        self,
        is_home: bool,
        team_score_increment: int,
        opponent_score_increment: int,
        points_earned_increment: int,
    ):
        """
        Process a new match completely with all statistics.

        :param is_home: Whether the team is playing at home
        :param team_score_increment: Goals scored by the team
        :param opponent_score_increment: Goals scored by the opponent
        :param points_earned_increment: Points earned from the match
        :returns: The updated team stat entity
        """
        # Calculate match statistics
        goal_difference = team_score_increment - opponent_score_increment

        # Update overall statistics
        self.overall_goals_for += team_score_increment
        self.overall_goals_against += opponent_score_increment
        self.overall_goals_difference += goal_difference
        self.overall_points += points_earned_increment

        # Update home/away specific statistics
        if is_home:
            self.home_goals_for += team_score_increment
            self.home_goals_against += opponent_score_increment
            self.home_goals_difference += goal_difference
            self.home_points += points_earned_increment
        else:
            self.away_goals_for += team_score_increment
            self.away_goals_against += opponent_score_increment
            self.away_goals_difference += goal_difference
            self.away_points += points_earned_increment

    def append_overall_point(self, point: int):
        """
        Append a point to the overall cumulative points.

        :param point: Points to append to the overall cumulative points
        """
        last_point = self.overall_cumulative_points[-1] if self.overall_cumulative_points else 0
        self.overall_cumulative_points.append(last_point + point)

    def append_home_point(self, point: int):
        """
        Append a point to the home cumulative points.

        :param point: Points to append to the home cumulative points
        """
        last_point = self.home_cumulative_points[-1] if self.home_cumulative_points else 0
        self.home_cumulative_points.append(last_point + point)

    def append_away_point(self, point: int):
        """
        Append a point to the away cumulative points.

        :param point: Points to append to the away cumulative points
        """
        last_point = self.away_cumulative_points[-1] if self.away_cumulative_points else 0
        self.away_cumulative_points.append(last_point + point)

    def compare_overall(
        self,
        target: Self,
        home_match: MatchEntity | None,
        away_match: MatchEntity | None,
    ) -> int:
        """
        Compare overall standings between two teams using football ranking criteria.

        Ranking order: Points > Goal Difference > Goals Scored > Head-to-head > Away goals

        :param target: Target team to compare
        :param home_match: Home match entity for head-to-head comparison (optional)
        :param away_match: Away match entity for head-to-head comparison (optional)
        :returns: 1 if self ranks higher, -1 if target ranks higher, 0 if equal
        """
        # Compare points
        points_comparison = compare_ints(self.overall_points, target.overall_points)
        if points_comparison != 0:
            return points_comparison

        # Compare goal difference
        goal_diff_comparison = compare_ints(
            self.overall_goals_difference, target.overall_goals_difference
        )
        if goal_diff_comparison != 0:
            return goal_diff_comparison

        # Compare goals scored
        goals_scored_comparison = compare_ints(
            self.overall_goals_for, target.overall_goals_for
        )
        if goals_scored_comparison != 0:
            return goals_scored_comparison

        if home_match is None and away_match is None:
            return 0
        elif home_match is not None and not self.check_is_home_match(home_match):
            raise ValueError(
                f"Home match {home_match.id} does not belong to team {self.team_id}"
            )
        elif away_match is not None and not self.check_is_away_match(away_match):
            raise ValueError(
                f"Away match {away_match.id} does not belong to team {self.team_id}"
            )
        else:
            # Calculate head-to-head points
            self_h2h_points = home_match.home_point if home_match else 0
            self_h2h_points += away_match.away_point if away_match else 0
            target_h2h_points = home_match.away_point if home_match else 0
            target_h2h_points += away_match.home_point if away_match else 0

            h2h_points_comparison = compare_ints(self_h2h_points, target_h2h_points)
            if h2h_points_comparison != 0:
                return h2h_points_comparison

            # If points are equal, compare away goals in head-to-head
            return (
                compare_ints(
                    away_match.away_team_score,
                    home_match.away_team_score,
                )
                if home_match is not None and away_match is not None
                else (home_match is None) - (away_match is None)
            )

    def compare_home(self, target: Self) -> int:
        """
        Compare home standings between two teams.

        Ranking order: Home Points > Home Goal Difference > Home Goals Scored

        :param target: Target team to compare
        :returns: 1 if team_a ranks higher, -1 if team_b ranks higher, 0 if equal
        """
        # Compare home points
        points_comparison = compare_ints(self.home_points, target.home_points)
        if points_comparison != 0:
            return points_comparison

        # Compare home goal difference
        goal_diff_comparison = compare_ints(
            self.home_goals_difference, target.home_goals_difference
        )
        if goal_diff_comparison != 0:
            return goal_diff_comparison

        # Compare home goals scored
        return compare_ints(self.home_goals_for, target.home_goals_for)

    def compare_away(self, target: Self) -> int:
        """
        Compare away standings between two teams.

        Ranking order: Away Points > Away Goal Difference > Away Goals Scored

        :param target: Target team to compare
        :returns: 1 if team_a ranks higher, -1 if team_b ranks higher, 0 if equal
        """
        # Compare away points
        points_comparison = compare_ints(self.away_points, target.away_points)
        if points_comparison != 0:
            return points_comparison

        # Compare away goal difference
        goal_diff_comparison = compare_ints(
            self.away_goals_difference, target.away_goals_difference
        )
        if goal_diff_comparison != 0:
            return goal_diff_comparison

        # Compare away goals scored
        return compare_ints(self.away_goals_for, target.away_goals_for)
