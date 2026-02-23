from sqlalchemy import String, ForeignKey, Integer, ARRAY, Double
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.repository.entities.base import PulseliveEntity
from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.staffs import StaffEntity
from football_data_manager.repository.entities.teams import TeamEntity

TEAM_STATS_TABLE_NAME = "team_stats"


class TeamStatEntity(PulseliveEntity):
    """
    Team statistics entity model with comprehensive match performance data.

    :ivar away_cumulative_points: Cumulative points progression in away matches
    :ivar ground_id: Foreign key to home ground entity
    :ivar manager_id: Foreign key to team manager entity (optional)
    :ivar season_id: Foreign key to season entity
    :ivar team_id: Foreign key to team entity
    """

    __tablename__ = TEAM_STATS_TABLE_NAME

    away_cumulative_points: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    away_goals_against: Mapped[int] = mapped_column(Integer, nullable=False)
    away_goals_for: Mapped[int] = mapped_column(Integer, nullable=False)
    away_goals_difference: Mapped[int] = mapped_column(Integer, nullable=False)
    away_matches: Mapped[int] = mapped_column(Integer, nullable=False)
    away_matches_drawn: Mapped[int] = mapped_column(Integer, nullable=False)
    away_matches_lost: Mapped[int] = mapped_column(Integer, nullable=False)
    away_matches_won: Mapped[int] = mapped_column(Integer, nullable=False)
    away_points: Mapped[int] = mapped_column(Integer, nullable=False)
    away_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ground_id: Mapped[str | None] = mapped_column(
        String,
        ForeignKey(GroundEntity.id, ondelete="SET NULL", onupdate="RESTRICT"),
        nullable=True,
    )
    home_cumulative_points: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    home_goals_against: Mapped[int] = mapped_column(Integer, nullable=False)
    home_goals_for: Mapped[int] = mapped_column(Integer, nullable=False)
    home_goals_difference: Mapped[int] = mapped_column(Integer, nullable=False)
    home_matches: Mapped[int] = mapped_column(Integer, nullable=False)
    home_matches_drawn: Mapped[int] = mapped_column(Integer, nullable=False)
    home_matches_lost: Mapped[int] = mapped_column(Integer, nullable=False)
    home_matches_won: Mapped[int] = mapped_column(Integer, nullable=False)
    home_points: Mapped[int] = mapped_column(Integer, nullable=False)
    home_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    manager_id: Mapped[str | None] = mapped_column(String, ForeignKey(StaffEntity.id), nullable=True)
    overall_cumulative_points: Mapped[list[int]] = mapped_column(ARRAY(Integer), nullable=False)
    overall_goals_against: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_goals_for: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_goals_difference: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_matches: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_matches_drawn: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_matches_lost: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_matches_won: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_points: Mapped[int] = mapped_column(Integer, nullable=False)
    overall_position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # fmt: off
    overall_stat_attack_corners: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_attack_crosses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_attack_crosses_successful: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_attack_expected_assists: Mapped[float | None] = mapped_column(Double, nullable=True)
    overall_stat_attack_expected_goals: Mapped[float | None] = mapped_column(Double, nullable=True)
    overall_stat_attack_long_balls: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_attack_long_balls_successful: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_attack_passes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_attack_passes_successful: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_attack_shots_on_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_attack_total_shots: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_attack_touches_in_opposition_box: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_average_possession: Mapped[float | None] = mapped_column(Double, nullable=True)
    overall_stat_defense_blocks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_clean_sheets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_clearances: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_duels_aerial_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_duels_aerial_won: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_duels_ground_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_duels_ground_won: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_duels_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_duels_won: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_interceptions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_saves: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_saves_penalty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_tackles: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_defense_tackles_successful: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_discipline_fouls: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_discipline_red_cards: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_discipline_red_cards_direct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    overall_stat_discipline_yellow_cards: Mapped[int | None] = mapped_column(Integer, nullable=True)
    momentum: Mapped[float | None] = mapped_column(Double, nullable=True)
    # fmt: on
    season_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(SeasonEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    team_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )

    def __init__(
        self,
        ground: GroundEntity | None,
        season: SeasonEntity,
        team: TeamEntity,
    ):
        """
        Initialize a new team stat entity.

        :param ground: Home ground entity (optional)
        :param season: Season entity
        :param team: Team entity
        """
        super().__init__(source_id=self.get_source_id(season, team))
        self.ground_id = ground.id if ground is not None else None
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

        :param season: Season entity
        :param team: Team entity
        :returns: Unique source ID combining season and team identifiers
        """
        return f"{season.source_id}_{team.source_id}"
