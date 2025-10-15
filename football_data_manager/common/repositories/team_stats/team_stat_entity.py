from typing import Self

from sqlalchemy import Column, String, ForeignKey, Integer, ARRAY, Double

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
    :ivar match_associations: List of all match associations
    :ivar overall_cumulative_points: Cumulative points progression in all matches
    :ivar overall_matches: Total matches played
    :ivar overall_matches_drawn: Total matches drawn
    :ivar overall_matches_lost: Total matches lost
    :ivar overall_matches_won: Total matches won
    :ivar overall_goals_against: Total goals conceded
    :ivar overall_goals_for: Total goals scored
    :ivar overall_goals_difference: Overall goal difference
    :ivar overall_points: Total points from all matches
    :ivar overall_position: Overall standings position
    :ivar overall_stat_attack_expected_assists: Expected assists value
    :ivar overall_stat_defense_clean_sheets: Number of clean sheets
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
    overall_position = Column(Integer, nullable=True)
    # fmt: off
    overall_stat_attack_corners = Column(Integer, nullable=True)  # cornersTakenInclShortCorners
    overall_stat_attack_crosses = Column(Integer, nullable=True)  # successfulCrossesAndCorners + unsuccessfulCrossesAndCorners
    overall_stat_attack_crosses_successful = Column(Integer, nullable=True)  # successfulCrossesAndCorners
    overall_stat_attack_expected_assists = Column(Double, nullable=True)  # expectedAssists
    overall_stat_attack_expected_goals = Column(Double, nullable=True)  # expectedGoals
    overall_stat_attack_long_balls = Column(Integer, nullable=True)  # successfulLongPasses + unsuccessfulLongPasses
    overall_stat_attack_long_balls_successful = Column(Integer, nullable=True)  # successfulLongPasses
    overall_stat_attack_passes = Column(Integer, nullable=True)  # totalPasses
    overall_stat_attack_passes_successful = Column(Integer, nullable=True)  # successfulShortPasses + successfulLongPasses
    overall_stat_attack_shots_on_target = Column(Integer, nullable=True)  # shotsOnTargetIncGoals
    overall_stat_attack_total_shots = Column(Integer, nullable=True) # totalShots
    overall_stat_attack_touches_in_opposition_box = Column(Integer, nullable=True)  # touchesInOppBox
    overall_stat_average_possession = Column(Double, nullable=True)  # possessionPercentage
    overall_stat_defense_blocks = Column(Integer, nullable=True)  # blockedShots
    overall_stat_defense_clean_sheets = Column(Integer, nullable=True)  # cleanSheets
    overall_stat_defense_clearances = Column(Integer, nullable=True)  # totalClearances
    overall_stat_defense_duels_aerial_total = Column(Integer, nullable=True)  # aerialDuels
    overall_stat_defense_duels_aerial_won = Column(Integer, nullable=True)  # aerialDuelsWon
    overall_stat_defense_duels_ground_total = Column(Integer, nullable=True)  # groundDuels
    overall_stat_defense_duels_ground_won = Column(Integer, nullable=True)  # groundDuelsWon
    overall_stat_defense_duels_total = Column(Integer, nullable=True)  # duels
    overall_stat_defense_duels_won = Column(Integer, nullable=True)  # duelsWon
    overall_stat_defense_interceptions = Column(Integer, nullable=True)  # interceptions
    overall_stat_defense_saves = Column(Integer, nullable=True)  # (shotsOnConcededInsideBox + shotsOnConcededOutsideBox - goalsConceded) + penaltiesSaved
    overall_stat_defense_saves_penalty = Column(Integer, nullable=True)  # penaltiesSaved
    overall_stat_defense_tackles = Column(Integer, nullable=True)  # timesTackled
    overall_stat_defense_tackles_successful = Column(Integer, nullable=True)  # tacklesWon
    overall_stat_discipline_fouls = Column(Integer, nullable=True)  # totalFoulsConceded
    overall_stat_discipline_red_cards = Column(Integer, nullable=True)  # totalRedCards
    overall_stat_discipline_red_cards_direct = Column(Integer, nullable=True)  # straightRedCards
    overall_stat_discipline_yellow_cards = Column(Integer, nullable=True)  # yellowCards
    # fmt: on
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
        self.ground_id = ground.id
        self.match_associations = []
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
        self.match_associations = []

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

        # Reset advanced stats
        self.overall_stat_attack_corners = 0
        self.overall_stat_attack_crosses = 0
        self.overall_stat_attack_crosses_successful = 0
        self.overall_stat_attack_expected_assists = 0.0
        self.overall_stat_attack_expected_goals = 0.0
        self.overall_stat_attack_long_balls = 0
        self.overall_stat_attack_long_balls_successful = 0
        self.overall_stat_attack_passes = 0
        self.overall_stat_attack_passes_successful = 0
        self.overall_stat_attack_shots_on_target = 0
        self.overall_stat_attack_total_shots = 0
        self.overall_stat_attack_touches_in_opposition_box = 0
        self.overall_stat_average_possession = 0.0
        self.overall_stat_defense_blocks = 0
        self.overall_stat_defense_clean_sheets = 0
        self.overall_stat_defense_clearances = 0
        self.overall_stat_defense_duels_aerial_total = 0
        self.overall_stat_defense_duels_aerial_won = 0
        self.overall_stat_defense_duels_ground_total = 0
        self.overall_stat_defense_duels_ground_won = 0
        self.overall_stat_defense_duels_total = 0
        self.overall_stat_defense_duels_won = 0
        self.overall_stat_defense_interceptions = 0
        self.overall_stat_defense_saves = 0
        self.overall_stat_defense_saves_penalty = 0
        self.overall_stat_defense_tackles = 0
        self.overall_stat_defense_tackles_successful = 0
        self.overall_stat_discipline_fouls = 0
        self.overall_stat_discipline_red_cards = 0
        self.overall_stat_discipline_red_cards_direct = 0
        self.overall_stat_discipline_yellow_cards = 0

    def update_match_result(
        self,
        is_home: bool,
        team_score: int,
        opponent_score: int,
    ):
        """
        Process a new match completely with all statistics.

        :param is_home: Whether the team is playing at home
        :param team_score: Goals scored by the team
        :param opponent_score: Goals scored by the opponent
        :returns: The updated team stat entity
        """
        # Calculate match statistics
        goal_difference = team_score - opponent_score
        points_earned = 3 if goal_difference > 0 else 1 if goal_difference == 0 else 0

        # Update overall statistics
        self.overall_goals_for += team_score
        self.overall_goals_against += opponent_score
        self.overall_goals_difference += goal_difference
        self.overall_points += points_earned
        self.overall_matches += 1
        self.overall_matches_won += points_earned == 3
        self.overall_matches_drawn += points_earned == 1
        self.overall_matches_lost += points_earned == 0
        self.append_overall_point(points_earned)

        # Update home/away specific statistics
        if is_home:
            self.home_goals_for += team_score
            self.home_goals_against += opponent_score
            self.home_goals_difference += goal_difference
            self.home_points += points_earned
            self.home_matches += 1
            self.home_matches_won += points_earned == 3
            self.home_matches_drawn += points_earned == 1
            self.home_matches_lost += points_earned == 0
            self.append_home_point(points_earned)
        else:
            self.away_goals_for += team_score
            self.away_goals_against += opponent_score
            self.away_goals_difference += goal_difference
            self.away_points += points_earned
            self.away_matches += 1
            self.away_matches_won += points_earned == 3
            self.away_matches_drawn += points_earned == 1
            self.away_matches_lost += points_earned == 0
            self.append_away_point(points_earned)

    def update_stats(
        self,
        attack_corners: int,
        attack_crosses: int,
        attack_crosses_successful: int,
        attack_expected_assists: float,
        attack_expected_goals: float,
        attack_long_balls: int,
        attack_long_balls_successful: int,
        attack_passes: int,
        attack_passes_successful: int,
        attack_shots_on_target: int,
        attack_total_shots: int,
        attack_touches_in_opposition_box: int,
        average_possession: float,
        defense_blocks: int,
        defense_clean_sheets: int,
        defense_clearances: int,
        defense_duels_aerial_total: int,
        defense_duels_aerial_won: int,
        defense_duels_ground_total: int,
        defense_duels_ground_won: int,
        defense_duels_total: int,
        defense_duels_won: int,
        defense_interceptions: int,
        defense_saves: int,
        defense_saves_penalty: int,
        defense_tackles: int,
        defense_tackles_successful: int,
        discipline_fouls: int,
        discipline_red_cards: int,
        discipline_red_cards_direct: int,
        discipline_yellow_cards: int,
    ):
        self.overall_stat_attack_corners = attack_corners
        self.overall_stat_attack_crosses = attack_crosses
        self.overall_stat_attack_crosses_successful = attack_crosses_successful
        self.overall_stat_attack_expected_assists = attack_expected_assists
        self.overall_stat_attack_expected_goals = attack_expected_goals
        self.overall_stat_attack_long_balls = attack_long_balls
        self.overall_stat_attack_long_balls_successful = attack_long_balls_successful
        self.overall_stat_attack_passes = attack_passes
        self.overall_stat_attack_passes_successful = attack_passes_successful
        self.overall_stat_attack_shots_on_target = attack_shots_on_target
        self.overall_stat_attack_total_shots = attack_total_shots
        self.overall_stat_attack_touches_in_opposition_box = (
            attack_touches_in_opposition_box
        )
        self.overall_stat_average_possession = average_possession
        self.overall_stat_defense_blocks = defense_blocks
        self.overall_stat_defense_clean_sheets = defense_clean_sheets
        self.overall_stat_defense_clearances = defense_clearances
        self.overall_stat_defense_duels_aerial_total = defense_duels_aerial_total
        self.overall_stat_defense_duels_aerial_won = defense_duels_aerial_won
        self.overall_stat_defense_duels_ground_total = defense_duels_ground_total
        self.overall_stat_defense_duels_ground_won = defense_duels_ground_won
        self.overall_stat_defense_duels_total = defense_duels_total
        self.overall_stat_defense_duels_won = defense_duels_won
        self.overall_stat_defense_interceptions = defense_interceptions
        self.overall_stat_defense_saves = defense_saves
        self.overall_stat_defense_saves_penalty = defense_saves_penalty
        self.overall_stat_defense_tackles = defense_tackles
        self.overall_stat_defense_tackles_successful = defense_tackles_successful
        self.overall_stat_discipline_fouls = discipline_fouls
        self.overall_stat_discipline_red_cards = discipline_red_cards
        self.overall_stat_discipline_red_cards_direct = discipline_red_cards_direct
        self.overall_stat_discipline_yellow_cards = discipline_yellow_cards

    def append_overall_point(self, point: int):
        """
        Append a point to the overall cumulative points.

        :param point: Points to append to the overall cumulative points
        """
        last_point = (
            self.overall_cumulative_points[-1] if self.overall_cumulative_points else 0
        )
        self.overall_cumulative_points.append(last_point + point)

    def append_home_point(self, point: int):
        """
        Append a point to the home cumulative points.

        :param point: Points to append to the home cumulative points
        """
        last_point = (
            self.home_cumulative_points[-1] if self.home_cumulative_points else 0
        )
        self.home_cumulative_points.append(last_point + point)

    def append_away_point(self, point: int):
        """
        Append a point to the away cumulative points.

        :param point: Points to append to the away cumulative points
        """
        last_point = (
            self.away_cumulative_points[-1] if self.away_cumulative_points else 0
        )
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
