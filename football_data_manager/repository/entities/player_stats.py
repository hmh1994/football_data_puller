from sqlalchemy import String, ForeignKey, Integer, Double
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.repository.entities.base import PulseliveEntity
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.teams import TeamEntity

PLAYER_STATS_TABLE_NAME = "player_stats"


class PlayerStatEntity(PulseliveEntity):
    """
    Entity model for player statistics with performance metrics.

    :ivar appearances: Number of appearances in matches
    :ivar number: Player's jersey number for the season
    :ivar player_id: Foreign key to the associated player
    :ivar season_id: Foreign key to the associated season
    :ivar team_id: Foreign key to the associated team
    """

    __tablename__ = PLAYER_STATS_TABLE_NAME

    # fmt: off
    appearances: Mapped[int] = mapped_column(Integer, nullable=False)
    defending_blocked: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_duels_aerial_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_duels_aerial_won: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_duels_ground_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_duels_ground_won: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_duels_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_duels_won: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_fouls_committed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_interceptions: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_possession_won_final_third: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_recoveries: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_tackles_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defending_tackles_won: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discipline_red_cards: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discipline_red_cards_direct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discipline_yellow_cards: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goalkeeping_clean_sheets: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goalkeeping_goals_conceded: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goalkeeping_goals_prevented: Mapped[float | None] = mapped_column(Double, nullable=True)
    goalkeeping_high_claim: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goalkeeping_penalties_faced: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goalkeeping_penalty_goals_conceded: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goalkeeping_penalty_saved: Mapped[int | None] = mapped_column(Integer, nullable=True)
    goalkeeping_saves: Mapped[int | None] = mapped_column(Integer, nullable=True)
    minutes_played: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    number: Mapped[int] = mapped_column(Integer, nullable=False)
    passing_assists: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passing_chances_created: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passing_crosses_successful: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passing_crosses_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passing_expected_assists: Mapped[float | None] = mapped_column(Double, nullable=True)
    passing_long_balls_accurate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passing_long_balls_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passing_passes_successful: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passing_passes_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    player_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    possession_dribble_successful: Mapped[int | None] = mapped_column(Integer, nullable=True)
    possession_dribble_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    possession_fouls_won: Mapped[int | None] = mapped_column(Integer, nullable=True)
    possession_touches: Mapped[int | None] = mapped_column(Integer, nullable=True)
    possession_touches_in_opposition_box: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_defending: Mapped[float] = mapped_column(Double, nullable=False, default=0.0)
    score_discipline: Mapped[float] = mapped_column(Double, nullable=False, default=0.0)
    score_dribbling: Mapped[float] = mapped_column(Double, nullable=False, default=0.0)
    score_overall: Mapped[float] = mapped_column(Double, nullable=False, default=0.0)
    score_passing: Mapped[float] = mapped_column(Double, nullable=False, default=0.0)
    score_shooting: Mapped[float] = mapped_column(Double, nullable=False, default=0.0)
    season_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(SeasonEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    shooting_expected_goals: Mapped[float | None] = mapped_column(Double, nullable=True)
    shooting_expected_goals_non_penalty: Mapped[float | None] = mapped_column(Double, nullable=True)
    shooting_expected_goals_on_target: Mapped[float | None] = mapped_column(Double, nullable=True)
    shooting_goals: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shooting_goals_penalty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shooting_penalties_taken: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shooting_shots: Mapped[int | None] = mapped_column(Integer, nullable=True)
    shooting_shots_on_target: Mapped[int | None] = mapped_column(Integer, nullable=True)
    team_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    # fmt: on

    def __init__(
        self,
        number: int,
        player: PlayerEntity,
        season: SeasonEntity,
        team: TeamEntity,
        appearances: int | None = None,
        defending_blocked: int | None = None,
        defending_duels_aerial_total: int | None = None,
        defending_duels_aerial_won: int | None = None,
        defending_duels_ground_total: int | None = None,
        defending_duels_ground_won: int | None = None,
        defending_duels_total: int | None = None,
        defending_duels_won: int | None = None,
        defending_fouls_committed: int | None = None,
        defending_interceptions: int | None = None,
        defending_possession_won_final_third: int | None = None,
        defending_recoveries: int | None = None,
        defending_tackles_total: int | None = None,
        defending_tackles_won: int | None = None,
        discipline_red_cards: int | None = None,
        discipline_red_cards_direct: int | None = None,
        discipline_yellow_cards: int | None = None,
        goalkeeping_clean_sheets: int | None = None,
        goalkeeping_goals_conceded: int | None = None,
        goalkeeping_goals_prevented: float | None = None,
        goalkeeping_high_claim: int | None = None,
        goalkeeping_penalties_faced: int | None = None,
        goalkeeping_penalty_goals_conceded: int | None = None,
        goalkeeping_penalty_saved: int | None = None,
        goalkeeping_saves: int | None = None,
        minutes_played: int = 0,
        passing_assists: int | None = None,
        passing_chances_created: int | None = None,
        passing_crosses_successful: int | None = None,
        passing_crosses_total: int | None = None,
        passing_expected_assists: float | None = None,
        passing_long_balls_accurate: int | None = None,
        passing_long_balls_total: int | None = None,
        passing_passes_successful: int | None = None,
        passing_passes_total: int | None = None,
        possession_dribble_successful: int | None = None,
        possession_dribble_total: int | None = None,
        possession_fouls_won: int | None = None,
        possession_touches: int | None = None,
        possession_touches_in_opposition_box: int | None = None,
        score_defending: float = 0.0,
        score_discipline: float = 0.0,
        score_dribbling: float = 0.0,
        score_overall: float = 0.0,
        score_passing: float = 0.0,
        score_shooting: float = 0.0,
        shooting_expected_goals: float | None = None,
        shooting_expected_goals_non_penalty: float | None = None,
        shooting_expected_goals_on_target: float | None = None,
        shooting_goals: int | None = None,
        shooting_goals_penalty: int | None = None,
        shooting_penalties_taken: int | None = None,
        shooting_shots: int | None = None,
        shooting_shots_on_target: int | None = None,
    ):
        """
        Initialize a new player stat entity.

        :param number: Player's jersey number for the season
        :param player: Player entity associated with the statistics
        :param season: Season entity for which statistics are recorded
        :param team: Team entity associated with the player
        """
        super().__init__(source_id=self.get_source_id(season, player))
        self.number = number
        self.player_id = player.id
        self.season_id = season.id
        self.team_id = team.id
        self.award_associations = []

        # Set all statistical fields
        self.appearances = appearances or 0
        self.defending_blocked = defending_blocked
        self.defending_duels_aerial_total = defending_duels_aerial_total
        self.defending_duels_aerial_won = defending_duels_aerial_won
        self.defending_duels_ground_total = defending_duels_ground_total
        self.defending_duels_ground_won = defending_duels_ground_won
        self.defending_duels_total = defending_duels_total
        self.defending_duels_won = defending_duels_won
        self.defending_fouls_committed = defending_fouls_committed
        self.defending_interceptions = defending_interceptions
        self.defending_possession_won_final_third = defending_possession_won_final_third
        self.defending_recoveries = defending_recoveries
        self.defending_tackles_total = defending_tackles_total
        self.defending_tackles_won = defending_tackles_won
        self.discipline_red_cards = discipline_red_cards
        self.discipline_red_cards_direct = discipline_red_cards_direct
        self.discipline_yellow_cards = discipline_yellow_cards
        self.goalkeeping_clean_sheets = goalkeeping_clean_sheets
        self.goalkeeping_goals_conceded = goalkeeping_goals_conceded
        self.goalkeeping_goals_prevented = goalkeeping_goals_prevented
        self.goalkeeping_high_claim = goalkeeping_high_claim
        self.goalkeeping_penalties_faced = goalkeeping_penalties_faced
        self.goalkeeping_penalty_goals_conceded = goalkeeping_penalty_goals_conceded
        self.goalkeeping_penalty_saved = goalkeeping_penalty_saved
        self.goalkeeping_saves = goalkeeping_saves
        self.minutes_played = minutes_played or 0
        self.passing_assists = passing_assists
        self.passing_chances_created = passing_chances_created
        self.passing_crosses_successful = passing_crosses_successful
        self.passing_crosses_total = passing_crosses_total
        self.passing_expected_assists = passing_expected_assists
        self.passing_long_balls_accurate = passing_long_balls_accurate
        self.passing_long_balls_total = passing_long_balls_total
        self.passing_passes_successful = passing_passes_successful
        self.passing_passes_total = passing_passes_total
        self.possession_dribble_successful = possession_dribble_successful
        self.possession_dribble_total = possession_dribble_total
        self.possession_fouls_won = possession_fouls_won
        self.possession_touches = possession_touches
        self.possession_touches_in_opposition_box = possession_touches_in_opposition_box
        self.score_defending = score_defending
        self.score_discipline = score_discipline
        self.score_dribbling = score_dribbling
        self.score_overall = score_overall
        self.score_passing = score_passing
        self.score_shooting = score_shooting
        self.shooting_expected_goals = shooting_expected_goals
        self.shooting_expected_goals_non_penalty = shooting_expected_goals_non_penalty
        self.shooting_expected_goals_on_target = shooting_expected_goals_on_target
        self.shooting_goals = shooting_goals
        self.shooting_goals_penalty = shooting_goals_penalty
        self.shooting_penalties_taken = shooting_penalties_taken
        self.shooting_shots = shooting_shots
        self.shooting_shots_on_target = shooting_shots_on_target

    @staticmethod
    def get_source_id(season: SeasonEntity, player: PlayerEntity) -> str:
        """
        Generate a unique source ID for the player stat entity.

        :param season: Season entity
        :param player: Player entity
        :returns: Unique source ID combining season and player identifiers
        """
        return f"{season.source_id}_{player.source_id}"
