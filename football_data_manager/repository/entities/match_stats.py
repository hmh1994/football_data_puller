from sqlalchemy import Integer, Double, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.repository.entities.base import PulseliveEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.teams import TeamEntity

MATCH_STATS_TABLE_NAME = "match_stats"


class MatchStatEntity(PulseliveEntity):
    """
    Entity model for comprehensive match statistics for teams.

    :ivar big_chances: Total big chances created
    :ivar big_chances_missed: Number of big chances missed
    :ivar corners: Number of corner kicks taken
    :ivar match_id: Foreign key to match entity
    :ivar team_id: Foreign key to team entity
    """

    __tablename__ = MATCH_STATS_TABLE_NAME

    # fmt: off
    big_chances: Mapped[int] = mapped_column(Integer, nullable=False)
    big_chances_missed: Mapped[int] = mapped_column(Integer, nullable=False)
    corners: Mapped[int] = mapped_column(Integer, nullable=False)
    defense_blocks: Mapped[int] = mapped_column(Integer, nullable=False)
    defense_clearances: Mapped[int] = mapped_column(Integer, nullable=False)
    defense_interceptions: Mapped[int] = mapped_column(Integer, nullable=False)
    defense_keeper_saves: Mapped[int] = mapped_column(Integer, nullable=False)
    defense_tackles_total: Mapped[int] = mapped_column(Integer, nullable=False)
    defense_tackles_won: Mapped[int] = mapped_column(Integer, nullable=False)
    discipline_red_cards: Mapped[int] = mapped_column(Integer, nullable=False)
    discipline_yellow_cards: Mapped[int] = mapped_column(Integer, nullable=False)
    duels_aerial_total: Mapped[int] = mapped_column(Integer, nullable=False)
    duels_aerial_won: Mapped[int] = mapped_column(Integer, nullable=False)
    duels_dribbles_successful: Mapped[int] = mapped_column(Integer, nullable=False)
    duels_dribbles_total: Mapped[int] = mapped_column(Integer, nullable=False)
    duels_ground_total: Mapped[int] = mapped_column(Integer, nullable=False)
    duels_ground_won: Mapped[int] = mapped_column(Integer, nullable=False)
    duels_total: Mapped[int] = mapped_column(Integer, nullable=False)
    duels_won: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_goals: Mapped[float] = mapped_column(Double, nullable=False)
    expected_goals_non_penalty: Mapped[float] = mapped_column(Double, nullable=False)
    expected_goals_on_target: Mapped[float] = mapped_column(Double, nullable=False)
    fouls_committed: Mapped[int] = mapped_column(Integer, nullable=False)
    match_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    passes_accurate: Mapped[int] = mapped_column(Integer, nullable=False)
    passes_accurate_crosses: Mapped[int] = mapped_column(Integer, nullable=False)
    passes_accurate_long_balls: Mapped[int] = mapped_column(Integer, nullable=False)
    passes_offsides: Mapped[int] = mapped_column(Integer, nullable=False)
    passes_opposition_half: Mapped[int] = mapped_column(Integer, nullable=False)
    passes_own_half: Mapped[int] = mapped_column(Integer, nullable=False)
    passes_throws: Mapped[int] = mapped_column(Integer, nullable=False)
    passes_total: Mapped[int] = mapped_column(Integer, nullable=False)
    passes_total_crosses: Mapped[int] = mapped_column(Integer, nullable=False)
    passes_total_long_balls: Mapped[int] = mapped_column(Integer, nullable=False)
    passes_touches_in_opposition_box: Mapped[int] = mapped_column(Integer, nullable=False)
    possession: Mapped[float] = mapped_column(Double, nullable=False)
    shots_blocked: Mapped[int] = mapped_column(Integer, nullable=False)
    shots_hit_woodwork: Mapped[int] = mapped_column(Integer, nullable=False)
    shots_inside_box: Mapped[int] = mapped_column(Integer, nullable=False)
    shots_off_target: Mapped[int] = mapped_column(Integer, nullable=False)
    shots_on_target: Mapped[int] = mapped_column(Integer, nullable=False)
    shots_outside_box: Mapped[int] = mapped_column(Integer, nullable=False)
    shots_total: Mapped[int] = mapped_column(Integer, nullable=False)
    team_id: Mapped[str] = mapped_column(
        String,
        ForeignKey(TeamEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    # fmt: on

    def __init__(
        self,
        big_chances: int,
        big_chances_missed: int,
        corners: int,
        defense_blocks: int,
        defense_clearances: int,
        defense_interceptions: int,
        defense_keeper_saves: int,
        defense_tackles_total: int,
        defense_tackles_won: int,
        discipline_red_cards: int,
        discipline_yellow_cards: int,
        duels_aerial_total: int,
        duels_aerial_won: int,
        duels_dribbles_successful: int,
        duels_dribbles_total: int,
        duels_ground_total: int,
        duels_ground_won: int,
        duels_total: int,
        duels_won: int,
        expected_goals: float,
        expected_goals_non_penalty: float,
        expected_goals_on_target: float,
        fouls_committed: int,
        passes_accurate: int,
        passes_accurate_crosses: int,
        passes_accurate_long_balls: int,
        passes_offsides: int,
        passes_opposition_half: int,
        passes_own_half: int,
        passes_throws: int,
        passes_total: int,
        passes_total_crosses: int,
        passes_total_long_balls: int,
        passes_touches_in_opposition_box: int,
        possession: float,
        shots_blocked: int,
        shots_hit_woodwork: int,
        shots_inside_box: int,
        shots_off_target: int,
        shots_on_target: int,
        shots_outside_box: int,
        shots_total: int,
        match: MatchEntity,
        team: TeamEntity,
    ):
        """
        Initialize a new match stat entity.

        :param match: Match entity for which statistics are recorded
        :param team: Team entity whose statistics are recorded
        """
        super().__init__(source_id=self.get_source_id(match, team))
        self.big_chances = big_chances
        self.big_chances_missed = big_chances_missed
        self.corners = corners
        self.defense_blocks = defense_blocks
        self.defense_clearances = defense_clearances
        self.defense_interceptions = defense_interceptions
        self.defense_keeper_saves = defense_keeper_saves
        self.defense_tackles_total = defense_tackles_total
        self.defense_tackles_won = defense_tackles_won
        self.discipline_red_cards = discipline_red_cards
        self.discipline_yellow_cards = discipline_yellow_cards
        self.duels_aerial_total = duels_aerial_total
        self.duels_aerial_won = duels_aerial_won
        self.duels_dribbles_successful = duels_dribbles_successful
        self.duels_dribbles_total = duels_dribbles_total
        self.duels_ground_total = duels_ground_total
        self.duels_ground_won = duels_ground_won
        self.duels_total = duels_total
        self.duels_won = duels_won
        self.expected_goals = expected_goals
        self.expected_goals_non_penalty = expected_goals_non_penalty
        self.expected_goals_on_target = expected_goals_on_target
        self.fouls_committed = fouls_committed
        self.match_id = match.id
        self.passes_accurate = passes_accurate
        self.passes_accurate_crosses = passes_accurate_crosses
        self.passes_accurate_long_balls = passes_accurate_long_balls
        self.passes_offsides = passes_offsides
        self.passes_opposition_half = passes_opposition_half
        self.passes_own_half = passes_own_half
        self.passes_throws = passes_throws
        self.passes_total = passes_total
        self.passes_total_crosses = passes_total_crosses
        self.passes_total_long_balls = passes_total_long_balls
        self.passes_touches_in_opposition_box = passes_touches_in_opposition_box
        self.possession = possession
        self.shots_blocked = shots_blocked
        self.shots_hit_woodwork = shots_hit_woodwork
        self.shots_inside_box = shots_inside_box
        self.shots_off_target = shots_off_target
        self.shots_on_target = shots_on_target
        self.shots_outside_box = shots_outside_box
        self.shots_total = shots_total
        self.team_id = team.id

    @staticmethod
    def get_source_id(match: MatchEntity, team: TeamEntity) -> str:
        """
        Generate a unique source ID for the match stat entity.

        :param match: Match entity
        :param team: Team entity
        :returns: Unique source ID combining match and team identifiers
        """
        return f"{match.source_id}_{team.source_id}"
