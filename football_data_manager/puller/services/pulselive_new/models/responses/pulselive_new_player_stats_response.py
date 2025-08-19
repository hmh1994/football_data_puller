from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewPlayerStatsResponse(CamelCaseModel):
    """
    Player statistics response from PulseLive API.

    Contains comprehensive player performance statistics for a specific season
    including goals, assists, appearances, and detailed performance metrics.

    :ivar appearances: Number of appearances in matches
    :ivar blocked_shots: Number of shots blocked by the player
    :ivar aerial_duels: Total number of aerial duels
    :ivar aerial_duels_won: Number of aerial duels won
    :ivar ground_duels: Total number of ground duels
    :ivar ground_duels_won: Number of ground duels won
    :ivar duels: Total number of duels
    :ivar duels_won: Number of duels won
    :ivar total_fouls_conceded: Total fouls committed
    :ivar interceptions: Number of interceptions made
    :ivar possession_won_final_third: Possessions won in final third
    :ivar recoveries: Number of ball recoveries
    :ivar total_tackles: Total number of tackles attempted
    :ivar tackles_won: Number of successful tackles
    :ivar total_red_cards: Total red cards received
    :ivar straight_red_cards: Direct red cards received
    :ivar yellow_cards: Yellow cards received
    :ivar clean_sheets: Number of clean sheets (for goalkeepers)
    :ivar goals_conceded: Number of goals conceded (for goalkeepers)
    :ivar expected_goals_on_target_conceded: Expected goals on target conceded
    :ivar catches: High claims/catches made
    :ivar penalties_faced: Number of penalties faced
    :ivar penalty_goals_conceded: Penalty goals conceded
    :ivar saves_made: Number of saves made
    :ivar successful_long_passes: Number of successful long passes
    :ivar unsuccessful_long_passes: Number of unsuccessful long passes
    :ivar goal_assists: Number of goal assists
    :ivar key_passes_attempt_assists: Key passes that could have been assists
    :ivar expected_assists: Expected assists value
    :ivar successful_short_passes: Number of successful short passes
    :ivar total_passes: Total number of passes attempted
    :ivar successful_crosses_and_corners: Successful crosses and corners
    :ivar unsuccessful_crosses_and_corners: Unsuccessful crosses and corners
    :ivar successful_dribbles: Number of successful dribbles
    :ivar unsuccessful_dribbles: Number of unsuccessful dribbles
    :ivar total_fouls_won: Total fouls won
    :ivar touches: Total number of touches
    :ivar total_touches_in_opposition_box: Touches in opposition box
    :ivar expected_goals: Expected goals value
    :ivar penalties_taken: Number of penalties taken
    :ivar expected_goals_on_target: Expected goals on target
    :ivar goals: Number of goals scored
    :ivar penalty_goals: Number of penalty goals scored
    :ivar total_shots: Total number of shots
    :ivar shots_on_target_inc_goals: Shots on target including goals
    """

    # Basic stats
    appearances: float | None = None

    # Defending stats
    blocked_shots: float | None = None
    aerial_duels: float | None = None
    aerial_duels_won: float | None = None
    ground_duels: float | None = None
    ground_duels_won: float | None = None
    duels: float | None = None
    duels_won: float | None = None
    total_fouls_conceded: float | None = None
    interceptions: float | None = None
    possession_won_final_third: float | None = None
    recoveries: float | None = None
    total_tackles: float | None = None
    tackles_won: float | None = None

    # Discipline stats
    total_red_cards: float | None = None
    straight_red_cards: float | None = None
    yellow_cards: float | None = None

    # Goalkeeping stats
    clean_sheets: float | None = None
    goals_conceded: float | None = None
    expected_goals_on_target_conceded: float | None = None
    catches: float | None = None
    penalties_faced: float | None = None
    penalty_goals_conceded: float | None = None
    saves_made: float | None = None

    # Passing stats
    successful_long_passes: float | None = None
    unsuccessful_long_passes: float | None = None
    goal_assists: float | None = None
    key_passes_attempt_assists: float | None = None
    expected_assists: float | None = None
    successful_short_passes: float | None = None
    total_passes: float | None = None
    successful_crosses_and_corners: float | None = None
    unsuccessful_crosses_and_corners: float | None = None

    # Possession stats
    successful_dribbles: float | None = None
    unsuccessful_dribbles: float | None = None
    total_fouls_won: float | None = None
    touches: float | None = None
    total_touches_in_opposition_box: float | None = None

    # Shooting stats
    expected_goals: float | None = None
    penalties_taken: float | None = None
    expected_goals_on_target: float | None = None
    goals: float | None = None
    penalty_goals: float | None = None
    total_shots: float | None = None
    shots_on_target_inc_goals: float | None = None
