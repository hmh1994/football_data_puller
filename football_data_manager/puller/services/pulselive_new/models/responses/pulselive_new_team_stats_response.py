from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewTeamStatsResponse(CamelCaseModel):
    """
    Team statistics response from PulseLive API.

    Contains comprehensive team performance statistics for a specific season
    including goals, shots, passes, defensive actions, set pieces, and other match events.

    :ivar duels_lost: Number of duels lost
    :ivar penalties_saved: Number of penalties saved
    :ivar blocked_shots: Number of shots blocked
    :ivar shots_on_target_incl_goals: Shots on target including goals
    :ivar expected_goals_on_target: Expected goals on target value
    :ivar games_played: Number of games played
    :ivar crossing_accuracy: Crossing accuracy percentage
    :ivar total_passes: Total number of passes
    :ivar goals: Number of goals scored
    :ivar offsides: Number of offside incidents
    :ivar away_goals: Goals scored away from home
    :ivar tackle_success: Tackle success percentage
    :ivar red_card_2nd_yellow: Second yellow card resulting in red
    :ivar obox_blocked: Shots blocked outside the box
    :ivar index: Team performance index
    :ivar passing_accuracy: Passing accuracy percentage
    :ivar ibox_target: Shots on target from inside the box
    :ivar aerial_duels_lost: Aerial duels lost
    :ivar goals_conceded_outside_box: Goals conceded from outside the box
    :ivar own_goals_accrued: Own goals scored in favor
    :ivar ground_duels_won: Ground duels won
    :ivar successful_corners_into_box: Successful corners delivered into box
    :ivar penalty_goals_conceded: Penalty goals conceded
    :ivar expected_goals_on_target_conceded: Expected goals on target conceded
    :ivar key_passes_attempt_assists: Key passes attempting assists
    :ivar successful_launches: Successful long launches
    :ivar total_fouls_won: Total fouls won
    :ivar recoveries: Number of ball recoveries
    :ivar points_gained_from_losing_positions: Points gained from losing positions
    :ivar passing_percent_opp_half: Passing percentage in opponent half
    :ivar shots_on_conceded_inside_box: Shots on target conceded inside box
    :ivar right_foot_goals: Goals scored with right foot
    :ivar left_foot_goals: Goals scored with left foot
    :ivar unsuccessful_dribbles: Unsuccessful dribbling attempts
    :ivar unsuccessful_crosses_and_corners: Unsuccessful crosses and corners
    :ivar other_goals: Goals scored by other means (head, etc.)
    :ivar times_tackled: Number of times tackled
    :ivar freekick_total: Total free kicks
    :ivar open_play_passes: Passes in open play
    :ivar gk_successful_distribution: Successful goalkeeper distribution
    :ivar shots_off_target_incl_woodwork: Shots off target including woodwork
    :ivar total_losses_of_possession: Total losses of possession
    :ivar tackles_won: Number of tackles won
    :ivar attempts_from_set_pieces: Attempts from set pieces
    :ivar total_shots_conceded: Total shots conceded
    :ivar total_fouls_conceded: Total fouls conceded
    :ivar unsuccessful_corners_into_box: Unsuccessful corners into box
    :ivar successful_long_passes: Successful long passes
    :ivar clearances_off_the_line: Clearances off the goal line
    :ivar throw_ins_to_own_player: Throw-ins to own player
    :ivar touches_in_opp_box: Touches in opponent's box
    :ivar hit_woodwork: Shots that hit the woodwork
    :ivar successful_passes_own_half: Successful passes in own half
    :ivar points_dropped_from_winning_positions: Points dropped from winning positions
    :ivar own_goals_conceded: Own goals conceded
    :ivar handballs_conceded: Handballs conceded
    :ivar unsuccessful_long_passes: Unsuccessful long passes
    :ivar unsuccessful_passes_own_half: Unsuccessful passes in own half
    :ivar successful_crosses_open_play: Successful crosses in open play
    :ivar expected_assists: Expected assists value
    :ivar total_red_cards: Total red cards received
    :ivar expected_goals_freekick: Expected goals from free kicks
    :ivar catches: High catches made
    :ivar overruns: Number of overruns
    :ivar unsuccessful_passes_opposition_half: Unsuccessful passes in opposition half
    :ivar total_shots: Total shots taken
    :ivar unsuccessful_short_passes: Unsuccessful short passes
    :ivar goal_assists: Number of goal assists
    :ivar successful_layoffs: Successful layoffs
    :ivar foul_won_penalty: Fouls won resulting in penalty
    :ivar unsuccessful_crosses_open_play: Unsuccessful crosses in open play
    :ivar goal_kicks: Number of goal kicks
    :ivar corners_taken_incl_short_corners: Corners taken including short corners
    :ivar aerial_duels: Total aerial duels
    :ivar clean_sheets: Number of clean sheets
    :ivar shooting_accuracy: Shooting accuracy percentage
    :ivar successful_crosses_and_corners: Successful crosses and corners
    :ivar unsuccessful_layoffs: Unsuccessful layoffs
    :ivar duels_won: Number of duels won
    :ivar penalties_conceded: Number of penalties conceded
    :ivar putthrough_blocked_distribution: Blocked distribution attempts
    :ivar successful_short_passes: Successful short passes
    :ivar throw_ins_to_opposition_player: Throw-ins to opposition player
    :ivar successful_open_play_passes: Successful passes in open play
    :ivar total_clearances: Total clearances made
    :ivar goals_conceded: Total goals conceded
    :ivar ground_duels_lost: Ground duels lost
    :ivar duels: Total number of duels
    :ivar putthrough_blocked_distribution_won: Blocked distribution won
    :ivar home_goals: Goals scored at home
    :ivar possession_percentage: Possession percentage
    :ivar obox_target: Shots on target from outside box
    :ivar tackles_lost: Number of tackles lost
    :ivar last_player_tackle: Last player tackles
    :ivar successful_passes_opposition_half: Successful passes in opposition half
    :ivar goals_conceded_inside_box: Goals conceded inside the box
    :ivar headed_goals: Goals scored with headers
    :ivar ibox_blocked: Shots blocked inside the box
    :ivar ground_duels: Total ground duels
    :ivar aerial_duels_won: Aerial duels won
    :ivar straight_red_cards: Direct red cards
    :ivar corners_won: Number of corners won
    :ivar successful_dribbles: Successful dribbling attempts
    :ivar blocks: Number of blocks made
    :ivar gk_unsuccessful_distribution: Unsuccessful goalkeeper distribution
    :ivar interceptions: Number of interceptions
    :ivar penalty_goals: Number of penalty goals scored
    :ivar unsuccessful_launches: Unsuccessful long launches
    :ivar foul_attempted_tackle: Fouls from attempted tackles
    :ivar shots_on_conceded_outside_box: Shots on target conceded outside box
    :ivar goal_conversion: Goal conversion rate
    :ivar expected_goals: Expected goals value
    :ivar yellow_cards: Number of yellow cards
    """

    # Match events
    duels_lost: float | None = None
    penalties_saved: float | None = None
    blocked_shots: float | None = None
    shots_on_target_incl_goals: float | None = None
    expected_goals_on_target: float | None = None
    games_played: float | None = None
    crossing_accuracy: float | None = None
    total_passes: float | None = None
    goals: float | None = None
    offsides: float | None = None
    away_goals: float | None = None
    tackle_success: float | None = None
    red_card_2nd_yellow: float | None = None
    obox_blocked: float | None = None
    index: float | None = None
    passing_accuracy: float | None = None
    ibox_target: float | None = None
    aerial_duels_lost: float | None = None
    goals_conceded_outside_box: float | None = None
    own_goals_accrued: float | None = None
    ground_duels_won: float | None = None
    successful_corners_into_box: float | None = None
    penalty_goals_conceded: float | None = None
    expected_goals_on_target_conceded: float | None = None
    key_passes_attempt_assists: float | None = None
    successful_launches: float | None = None
    total_fouls_won: float | None = None
    recoveries: float | None = None
    points_gained_from_losing_positions: float | None = None
    passing_percent_opp_half: float | None = None
    shots_on_conceded_inside_box: float | None = None
    right_foot_goals: float | None = None
    left_foot_goals: float | None = None
    unsuccessful_dribbles: float | None = None
    unsuccessful_crosses_and_corners: float | None = None
    other_goals: float | None = None
    times_tackled: float | None = None
    freekick_total: float | None = None
    open_play_passes: float | None = None
    gk_successful_distribution: float | None = None
    shots_off_target_incl_woodwork: float | None = None
    total_losses_of_possession: float | None = None
    tackles_won: float | None = None
    attempts_from_set_pieces: float | None = None
    total_shots_conceded: float | None = None
    total_fouls_conceded: float | None = None
    unsuccessful_corners_into_box: float | None = None
    successful_long_passes: float | None = None
    clearances_off_the_line: float | None = None
    throw_ins_to_own_player: float | None = None
    touches_in_opp_box: float | None = None
    hit_woodwork: float | None = None
    successful_passes_own_half: float | None = None
    points_dropped_from_winning_positions: float | None = None
    own_goals_conceded: float | None = None
    handballs_conceded: float | None = None
    unsuccessful_long_passes: float | None = None
    unsuccessful_passes_own_half: float | None = None
    successful_crosses_open_play: float | None = None
    expected_assists: float | None = None
    total_red_cards: float | None = None
    expected_goals_freekick: float | None = None
    catches: float | None = None
    overruns: float | None = None
    unsuccessful_passes_opposition_half: float | None = None
    total_shots: float | None = None
    unsuccessful_short_passes: float | None = None
    goal_assists: float | None = None
    successful_layoffs: float | None = None
    foul_won_penalty: float | None = None
    unsuccessful_crosses_open_play: float | None = None
    goal_kicks: float | None = None
    corners_taken_incl_short_corners: float | None = None
    aerial_duels: float | None = None
    clean_sheets: float | None = None
    shooting_accuracy: float | None = None
    successful_crosses_and_corners: float | None = None
    unsuccessful_layoffs: float | None = None
    duels_won: float | None = None
    penalties_conceded: float | None = None
    putthrough_blocked_distribution: float | None = None
    successful_short_passes: float | None = None
    throw_ins_to_opposition_player: float | None = None
    successful_open_play_passes: float | None = None
    total_clearances: float | None = None
    goals_conceded: float | None = None
    ground_duels_lost: float | None = None
    duels: float | None = None
    putthrough_blocked_distribution_won: float | None = None
    home_goals: float | None = None
    possession_percentage: float | None = None
    obox_target: float | None = None
    tackles_lost: float | None = None
    last_player_tackle: float | None = None
    successful_passes_opposition_half: float | None = None
    goals_conceded_inside_box: float | None = None
    headed_goals: float | None = None
    ibox_blocked: float | None = None
    ground_duels: float | None = None
    aerial_duels_won: float | None = None
    straight_red_cards: float | None = None
    corners_won: float | None = None
    successful_dribbles: float | None = None
    blocks: float | None = None
    gk_unsuccessful_distribution: float | None = None
    interceptions: float | None = None
    penalty_goals: float | None = None
    unsuccessful_launches: float | None = None
    foul_attempted_tackle: float | None = None
    shots_on_conceded_outside_box: float | None = None
    goal_conversion: float | None = None
    expected_goals: float | None = None
    yellow_cards: float | None = None