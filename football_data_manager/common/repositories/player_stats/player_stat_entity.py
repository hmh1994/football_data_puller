from sqlalchemy import Column, String, ForeignKey, Integer, Double

from football_data_manager.common.repositories.constants import (
    PLAYER_STATS_TABLE_NAME,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.repositories.pulselive_entity import (
    PulseliveEntity,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity


class PlayerStatEntity(PulseliveEntity):
    """
    Entity model for player statistics with performance metrics and awards.

    Represents comprehensive player performance statistics for a specific season
    and team, including goals, assists, appearances, and award associations.
    Extends PulseliveEntity to inherit source tracking functionality.

    :ivar id: Unique identifier for the player stat
    :ivar appearances: Number of appearances in matches
    :ivar assists: Number of assists provided
    :ivar award_associations: List of awards received during the season
    :ivar clean_sheets: Number of clean sheets (for goalkeepers)
    :ivar goals: Number of goals scored
    :ivar goals_conceded: Number of goals conceded (for goalkeepers)
    :ivar key_passes: Number of key passes made
    :ivar number: Player's jersey number for the season
    :ivar player_id: Foreign key to the associated player
    :ivar saves: Number of saves made (for goalkeepers)
    :ivar season_id: Foreign key to the associated season
    :ivar shots: Number of shots taken
    :ivar tackles: Number of tackles made
    :ivar team_id: Foreign key to the associated team
    :ivar source: Source of the entity data, set to PULSELIVE
    :ivar source_id: Unique identifier from the source
    :ivar created_at: Entity creation timestamp
    :ivar updated_at: Last modification timestamp
    """

    __tablename__ = PLAYER_STATS_TABLE_NAME

    # fmt: off
    appearances = Column(Integer, nullable=False)  # appearances
    defending_blocked = Column(Integer, nullable=True)  # blockedShots
    defending_duels_aerial_total = Column(Integer, nullable=True)  # aerialDuels
    defending_duels_aerial_won = Column(Integer, nullable=True)  # aerialDuelsWon
    defending_duels_ground_total = Column(Integer, nullable=True)  # groundDuels
    defending_duels_ground_won = Column(Integer, nullable=True)  # groundDuelsWon
    defending_duels_total = Column(Integer, nullable=True)  # duels
    defending_duels_won = Column(Integer, nullable=True)  # duelsWon
    defending_fouls_committed = Column(Integer, nullable=True)  # totalFoulsConceded
    defending_interceptions = Column(Integer, nullable=True)  # interceptions
    defending_possession_won_final_third = Column(Integer, nullable=True)
    defending_recoveries = Column(Integer, nullable=True)  # recoveries
    defending_tackles_total = Column(Integer, nullable=True)  # totalTackles
    defending_tackles_won = Column(Integer, nullable=True)  # tacklesWon
    discipline_red_cards = Column(Integer, nullable=True)  # totalRedCards
    discipline_red_cards_direct = Column(Integer, nullable=True)  # straightRedCards
    discipline_yellow_cards = Column(Integer, nullable=True)  # yellowCards
    goalkeeping_clean_sheets = Column(Integer, nullable=True)  # cleanSheets
    goalkeeping_goals_conceded = Column(Integer, nullable=True)  # goalsConceded
    goalkeeping_goals_prevented = Column(Double, nullable=True)  # expectedGoalsOnTargetConceded - goalsConceded
    goalkeeping_high_claim = Column(Integer, nullable=True)  # catches
    goalkeeping_penalties_faced = Column(Integer, nullable=True)  # penaltiesFaced
    goalkeeping_penalty_goals_conceded = Column(Integer, nullable=True)  # penaltyGoalsConceded
    goalkeeping_penalty_saved = Column(Integer, nullable=True)  # penaltiesFaced − penaltyGoalsConceded
    goalkeeping_saves = Column(Integer, nullable=True)  # savesMade
    number = Column(Integer, nullable=False)
    passing_long_balls_accurate = Column(Integer, nullable=True)  # successfulLongPasses
    passing_long_balls_total = Column(Integer, nullable=True)  # successfulLongPasses + unsuccessfulLongPasses
    passing_assists = Column(Integer, nullable=True)  # goalAssists
    passing_chances_created = Column(Integer, nullable=True)  # goalAssists + keyPassesAttemptAssists
    passing_expected_assists = Column(Double, nullable=True)  # expectedAssists
    passing_passes_successful = Column(Integer, nullable=True)  # successfulShortPasses + successfulLongPasses
    passing_passes_total = Column(Integer, nullable=True)  # totalPasses
    passing_crosses_successful = Column(Integer, nullable=True)  # successfulCrossesAndCorners
    passing_crosses_total = Column(Integer, nullable=True)  # successfulCrossesAndCorners + unsuccessfulCrossesAndCorners
    player_id = Column(
        String,
        ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    possession_dribble_total = Column(Integer, nullable=True)  # successfulDribbles + unsuccessfulDribbles
    possession_dribble_successful = Column(Integer, nullable=True)  # successfulDribbles
    possession_fouls_won = Column(Integer, nullable=True)  # totalFoulsWon
    possession_touches = Column(Integer, nullable=True)  # touches
    possession_touches_in_opposition_box = Column(Integer, nullable=True)  # totalTouchesInOppositionBox
    season_id = Column(
        String,
        ForeignKey(SeasonEntity.id, ondelete="CASCADE", onupdate="RESTRICT"),
        nullable=False,
    )
    shooting_expected_goals = Column(Double, nullable=True)  # expectedGoals
    shooting_expected_goals_non_penalty = Column(Double, nullable=True)  # expectedGoals - (0.79 * penaltiesTaken)
    shooting_expected_goals_on_target = Column(Double, nullable=True)  # expectedGoalsOnTarget
    shooting_goals = Column(Integer, nullable=True)  # goals
    shooting_goals_penalty = Column(Integer, nullable=True)  # penaltyGoals
    shooting_penalties_taken = Column(Integer, nullable=True)  # penaltiesTaken
    shooting_shots = Column(Integer, nullable=True)  # totalShots + blockedShots
    shooting_shots_on_target = Column(Integer, nullable=True)  # shotsOnTargetIncGoals
    minutes_played = Column(Integer, nullable=True)  # Total minutes played in season
    team_id = Column(
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
        passing_long_balls_accurate: int | None = None,
        passing_long_balls_total: int | None = None,
        passing_assists: int | None = None,
        passing_chances_created: int | None = None,
        passing_expected_assists: float | None = None,
        passing_passes_successful: int | None = None,
        passing_passes_total: int | None = None,
        passing_crosses_successful: int | None = None,
        passing_crosses_total: int | None = None,
        possession_dribble_total: int | None = None,
        possession_dribble_successful: int | None = None,
        possession_fouls_won: int | None = None,
        possession_touches: int | None = None,
        possession_touches_in_opposition_box: int | None = None,
        shooting_expected_goals: float | None = None,
        shooting_expected_goals_non_penalty: float | None = None,
        shooting_expected_goals_on_target: float | None = None,
        shooting_goals: int | None = None,
        shooting_goals_penalty: int | None = None,
        shooting_penalties_taken: int | None = None,
        shooting_shots: int | None = None,
        shooting_shots_on_target: int | None = None,
        minutes_played: int | None = None,
    ):
        """
        Initialize a new player stat entity.

        :param number: Player's jersey number for the season
        :param player: Player entity associated with the statistics
        :param season: Season entity for which statistics are recorded
        :param team: Team entity associated with the player
        :param appearances: Number of appearances in matches
        :param defending_blocked: Number of shots blocked by the player
        :param defending_duels_aerial_total: Total number of aerial duels
        :param defending_duels_aerial_won: Number of aerial duels won
        :param defending_duels_ground_total: Total number of ground duels
        :param defending_duels_ground_won: Number of ground duels won
        :param defending_duels_total: Total number of duels
        :param defending_duels_won: Number of duels won
        :param defending_fouls_committed: Total fouls committed
        :param defending_interceptions: Number of interceptions made
        :param defending_possession_won_final_third: Possessions won in final third
        :param defending_recoveries: Number of ball recoveries
        :param defending_tackles_total: Total number of tackles attempted
        :param defending_tackles_won: Number of successful tackles
        :param discipline_red_cards: Total red cards received
        :param discipline_red_cards_direct: Direct red cards received
        :param discipline_yellow_cards: Yellow cards received
        :param goalkeeping_clean_sheets: Number of clean sheets
        :param goalkeeping_goals_conceded: Number of goals conceded
        :param goalkeeping_goals_prevented: Goals prevented above expected
        :param goalkeeping_high_claim: High claims/catches made
        :param goalkeeping_penalties_faced: Number of penalties faced
        :param goalkeeping_penalty_goals_conceded: Penalty goals conceded
        :param goalkeeping_penalty_saved: Number of penalties saved
        :param goalkeeping_saves: Number of saves made
        :param passing_long_balls_accurate: Number of successful long passes
        :param passing_long_balls_total: Total long passes attempted
        :param passing_assists: Number of goal assists
        :param passing_chances_created: Total chances created
        :param passing_expected_assists: Expected assists value
        :param passing_passes_successful: Number of successful passes
        :param passing_passes_total: Total number of passes attempted
        :param passing_crosses_successful: Successful crosses and corners
        :param passing_crosses_total: Total crosses and corners attempted
        :param possession_dribble_total: Total dribbles attempted
        :param possession_dribble_successful: Number of successful dribbles
        :param possession_fouls_won: Total fouls won
        :param possession_touches: Total number of touches
        :param possession_touches_in_opposition_box: Touches in opposition box
        :param shooting_expected_goals: Expected goals value
        :param shooting_expected_goals_non_penalty: Expected goals excluding penalties
        :param shooting_expected_goals_on_target: Expected goals on target
        :param shooting_goals: Number of goals scored
        :param shooting_goals_penalty: Number of penalty goals scored
        :param shooting_penalties_taken: Number of penalties taken
        :param shooting_shots: Total number of shots
        :param shooting_shots_on_target: Shots on target including goals
        :param minutes_played: Total minutes played in season
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
        self.passing_long_balls_accurate = passing_long_balls_accurate
        self.passing_long_balls_total = passing_long_balls_total
        self.passing_assists = passing_assists
        self.passing_chances_created = passing_chances_created
        self.passing_expected_assists = passing_expected_assists
        self.passing_passes_successful = passing_passes_successful
        self.passing_passes_total = passing_passes_total
        self.passing_crosses_successful = passing_crosses_successful
        self.passing_crosses_total = passing_crosses_total
        self.possession_dribble_total = possession_dribble_total
        self.possession_dribble_successful = possession_dribble_successful
        self.possession_fouls_won = possession_fouls_won
        self.possession_touches = possession_touches
        self.possession_touches_in_opposition_box = possession_touches_in_opposition_box
        self.shooting_expected_goals = shooting_expected_goals
        self.shooting_expected_goals_non_penalty = shooting_expected_goals_non_penalty
        self.shooting_expected_goals_on_target = shooting_expected_goals_on_target
        self.shooting_goals = shooting_goals
        self.shooting_goals_penalty = shooting_goals_penalty
        self.shooting_penalties_taken = shooting_penalties_taken
        self.shooting_shots = shooting_shots
        self.shooting_shots_on_target = shooting_shots_on_target
        self.minutes_played = minutes_played

    @staticmethod
    def get_source_id(season: SeasonEntity, player: PlayerEntity) -> str:
        """
        Generate a unique source ID for the player stat entity.

        :param season: Season entity for which statistics are recorded
        :param player: Player entity associated with the statistics
        :returns: Unique source ID combining season and player identifiers
        """
        return f"{season.source_id}_{player.source_id}"
