from sqlalchemy import Column, Integer, Double, String, ForeignKey

from football_data_manager.common.repositories.constants import (
    MATCH_STATS_TABLE_NAME,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity


class MatchStatEntity(PulseliveEntity):
    """
    Entity model for comprehensive match statistics for teams.
    
    Represents detailed statistical data for a team's performance in a specific match,
    including passing, shooting, defensive, and possession metrics. Extends PulseliveEntity
    to inherit source tracking functionality.
    
    :ivar id: Unique identifier for the entity
    :ivar big_chances: Total big chances created (scored + missed)
    :ivar big_chances_missed: Number of big chances missed
    :ivar corners: Number of corner kicks taken
    :ivar defense_blocks: Number of defensive blocks by outfield players
    :ivar defense_clearances: Total number of clearances made
    :ivar defense_interceptions: Number of interceptions made
    :ivar defense_keeper_saves: Number of saves made by goalkeeper
    :ivar defense_tackles_total: Total number of tackles attempted
    :ivar defense_tackles_won: Number of successful tackles
    :ivar discipline_red_cards: Number of red cards received
    :ivar discipline_yellow_cards: Number of yellow cards received
    :ivar duels_aerial_total: Total aerial duels (won + lost)
    :ivar duels_aerial_won: Number of aerial duels won
    :ivar duels_dribbles_successful: Number of successful dribbles/contests
    :ivar duels_dribbles_total: Total number of dribble attempts
    :ivar duels_ground_total: Total ground duels (excluding aerial)
    :ivar duels_ground_won: Number of ground duels won
    :ivar duels_total: Total duels (won + lost)
    :ivar duels_won: Total number of duels won
    :ivar expected_goals: Expected goals (xG) value
    :ivar expected_goals_non_penalty: Expected goals excluding penalties
    :ivar expected_goals_on_target: Expected goals on target
    :ivar fouls_committed: Number of fouls committed
    :ivar match_id: Foreign key to match entity
    :ivar passes_accurate: Number of accurate passes
    :ivar passes_accurate_crosses: Number of accurate crosses
    :ivar passes_accurate_long_balls: Number of accurate long balls
    :ivar passes_offsides: Number of offside situations
    :ivar passes_opposition_half: Passes in opposition half (excluding crosses)
    :ivar passes_own_half: Passes in own half
    :ivar passes_throws: Number of throw-ins taken
    :ivar passes_total: Total number of passes attempted
    :ivar passes_total_crosses: Total number of crosses attempted
    :ivar passes_total_long_balls: Total number of long balls attempted
    :ivar passes_touches_in_opposition_box: Touches in opposition penalty box
    :ivar possession: Ball possession percentage
    :ivar shots_blocked: Number of shots blocked
    :ivar shots_hit_woodwork: Number of shots that hit woodwork
    :ivar shots_inside_box: Shots taken inside the penalty box
    :ivar shots_off_target: Number of shots off target
    :ivar shots_on_target: Number of shots on target
    :ivar shots_outside_box: Shots taken outside the penalty box
    :ivar shots_total: Total number of shots attempted
    :ivar team_id: Foreign key to team entity
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source system
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = MATCH_STATS_TABLE_NAME

    big_chances = Column(Integer, nullable=False)  # bigChanceScored + bigChanceMissed
    big_chances_missed = Column(Integer, nullable=False)  # bigChanceMissed
    corners = Column(Integer, nullable=False)  # cornerTaken
    defense_blocks = Column(Integer, nullable=False)  # outfielderBlock
    defense_clearances = Column(Integer, nullable=False)  # totalClearance
    defense_interceptions = Column(Integer, nullable=False)  # interception
    defense_keeper_saves = Column(Integer, nullable=False)  # saves
    defense_tackles_total = Column(Integer, nullable=False)  # totalTackle
    defense_tackles_won = Column(Integer, nullable=False)  # wonTackle
    discipline_red_cards = Column(Integer, nullable=False)  # totalRedCard
    discipline_yellow_cards = Column(Integer, nullable=False)  # totalYelCard
    duels_aerial_total = Column(Integer, nullable=False)  # aerialWon + aerialLost
    duels_aerial_won = Column(Integer, nullable=False)  # aerialWon
    duels_dribbles_successful = Column(Integer, nullable=False)  # wonContest
    duels_dribbles_total = Column(Integer, nullable=False)  # totalContest
    duels_ground_total = Column(
        Integer, nullable=False
    )  # duelWon + duelLost - aerialWon - aerialLost
    duels_ground_won = Column(Integer, nullable=False)  # duelWon - aerialWon
    duels_total = Column(Integer, nullable=False)  # duelWon + duelLost
    duels_won = Column(Integer, nullable=False)  # duelWon
    expected_goals = Column(Double, nullable=False)  # expectedGoals
    expected_goals_non_penalty = Column(
        Double, nullable=False
    )  # expectedGoals - (home.penaltyFaced * 0.79)
    expected_goals_on_target = Column(Double, nullable=False)  # expectedGoalsOnTarget
    fouls_committed = Column(Integer, nullable=False)  # fkFoulLost
    match_id = Column(String, ForeignKey(MatchEntity.id), nullable=False)
    passes_accurate = Column(Integer, nullable=False)  # accuratePass
    passes_accurate_crosses = Column(Integer, nullable=False)  # accurateCross
    passes_accurate_long_balls = Column(Integer, nullable=False)  # accurateLongBalls
    passes_offsides = Column(Integer, nullable=False)  # totalOffside
    passes_opposition_half = Column(
        Integer, nullable=False
    )  # accurateFwdZonePass - accurateCross
    passes_own_half = Column(Integer, nullable=False)  # accurateBackZonePass
    passes_throws = Column(Integer, nullable=False)  # totalThrows
    passes_total = Column(Integer, nullable=False)  # totalPass
    passes_total_crosses = Column(Integer, nullable=False)  # totalCross
    passes_total_long_balls = Column(Integer, nullable=False)  # totalLongBalls
    passes_touches_in_opposition_box = Column(
        Integer, nullable=False
    )  # touchesInOppBox
    possession = Column(Double, nullable=False)  # possessionPercentage
    shots_blocked = Column(Integer, nullable=False)  # blockedScoringAtt
    shots_hit_woodwork = Column(Integer, nullable=False)  # hitWoodwork
    shots_inside_box = Column(Integer, nullable=False)  # attemptsIbox
    shots_off_target = Column(Integer, nullable=False)  # shotOffTarget
    shots_on_target = Column(Integer, nullable=False)  # ontargetScoringAtt
    shots_outside_box = Column(Integer, nullable=False)  # attemptsObox
    shots_total = Column(Integer, nullable=False)  # totalScoringAtt
    team_id = Column(String, ForeignKey(TeamEntity.id), nullable=False)

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
        
        Creates comprehensive match statistics for a team's performance in a specific match.
        All statistical metrics are captured including attacking, defensive, passing, and possession data.
        
        :param big_chances: Total big chances created (scored + missed)
        :param big_chances_missed: Number of big chances missed
        :param corners: Number of corner kicks taken
        :param defense_blocks: Number of defensive blocks by outfield players
        :param defense_clearances: Total number of clearances made
        :param defense_interceptions: Number of interceptions made
        :param defense_keeper_saves: Number of saves made by goalkeeper
        :param defense_tackles_total: Total number of tackles attempted
        :param defense_tackles_won: Number of successful tackles
        :param discipline_red_cards: Number of red cards received
        :param discipline_yellow_cards: Number of yellow cards received
        :param duels_aerial_total: Total aerial duels (won + lost)
        :param duels_aerial_won: Number of aerial duels won
        :param duels_dribbles_successful: Number of successful dribbles/contests
        :param duels_dribbles_total: Total number of dribble attempts
        :param duels_ground_total: Total ground duels (excluding aerial)
        :param duels_ground_won: Number of ground duels won
        :param duels_total: Total duels (won + lost)
        :param duels_won: Total number of duels won
        :param expected_goals: Expected goals (xG) value
        :param expected_goals_non_penalty: Expected goals excluding penalties
        :param expected_goals_on_target: Expected goals on target
        :param fouls_committed: Number of fouls committed
        :param passes_accurate: Number of accurate passes
        :param passes_accurate_crosses: Number of accurate crosses
        :param passes_accurate_long_balls: Number of accurate long balls
        :param passes_offsides: Number of offside situations
        :param passes_opposition_half: Passes in opposition half (excluding crosses)
        :param passes_own_half: Passes in own half
        :param passes_throws: Number of throw-ins taken
        :param passes_total: Total number of passes attempted
        :param passes_total_crosses: Total number of crosses attempted
        :param passes_total_long_balls: Total number of long balls attempted
        :param passes_touches_in_opposition_box: Touches in opposition penalty box
        :param possession: Ball possession percentage
        :param shots_blocked: Number of shots blocked
        :param shots_hit_woodwork: Number of shots that hit woodwork
        :param shots_inside_box: Shots taken inside the penalty box
        :param shots_off_target: Number of shots off target
        :param shots_on_target: Number of shots on target
        :param shots_outside_box: Shots taken outside the penalty box
        :param shots_total: Total number of shots attempted
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
        
        Creates a composite source ID by combining the match and team source identifiers
        to ensure uniqueness for each team's statistics within a match.
        
        :param match: Match entity for which statistics are recorded
        :param team: Team entity whose statistics are recorded
        :returns: Unique source ID combining match and team identifiers
        """
        return f"{match.source_id}_{team.source_id}"
