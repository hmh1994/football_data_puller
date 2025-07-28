from sqlalchemy import Column, Integer, Double, String, ForeignKey

from football_data_manager.common.new_repositories.constants import (
    MATCH_STATS_TABLE_NAME,
)
from football_data_manager.common.new_repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.new_repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.new_repositories.teams.team_entity import TeamEntity


class MatchStatEntity(PulseliveEntity):
    """ """

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
        """ """
        return f"{match.source_id}_{team.source_id}"
