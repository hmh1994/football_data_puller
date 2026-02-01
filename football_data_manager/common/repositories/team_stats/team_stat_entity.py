from sqlalchemy import Column, String, ForeignKey, Integer, ARRAY, Double

from football_data_manager.common.repositories.constants import (
    TEAM_STATS_TABLE_NAME,
)
from football_data_manager.common.repositories.grounds.ground_entity import (
    GroundEntity,
)
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.staffs.staff_entity import StaffEntity
from football_data_manager.common.repositories.teams.team_entity import TeamEntity


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
    momentum = Column(Double, nullable=True)  # Team Momentum Index: 100 * tanh(β * (0.6*z(ΔPPM) + 0.4*z(ΔxG)))
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

        # Initialize overall statistics
        self.overall_cumulative_points = []
        self.overall_goals_for = 0
        self.overall_goals_against = 0
        self.overall_goals_difference = 0
        self.overall_matches = 0
        self.overall_matches_won = 0
        self.overall_matches_drawn = 0
        self.overall_matches_lost = 0
        self.overall_points = 0

        # Initialize home statistics
        self.home_cumulative_points = []
        self.home_goals_for = 0
        self.home_goals_against = 0
        self.home_goals_difference = 0
        self.home_matches = 0
        self.home_matches_won = 0
        self.home_matches_drawn = 0
        self.home_matches_lost = 0
        self.home_points = 0

        # Initialize away statistics
        self.away_cumulative_points = []
        self.away_goals_for = 0
        self.away_goals_against = 0
        self.away_goals_difference = 0
        self.away_matches = 0
        self.away_matches_won = 0
        self.away_matches_drawn = 0
        self.away_matches_lost = 0
        self.away_points = 0

        # Initialize advanced stats
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

        # Initialize positions
        self.overall_position = None
        self.home_position = None
        self.away_position = None

        # Initialize momentum
        self.momentum = None

    @staticmethod
    def get_source_id(season: SeasonEntity, team: TeamEntity) -> str:
        """
        Generate a unique source ID for the team stat entity.

        :param season: Season entity for which statistics are recorded
        :param team: Team entity associated with the statistics
        :returns: Unique source ID combining season and team identifiers
        """
        return f"{season.source_id}_{team.source_id}"

