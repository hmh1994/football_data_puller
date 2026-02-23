from typing import TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel


class TeamSimpleDict(TypedDict):
    """Simple team info used in statistics responses."""

    id: str
    name: str
    short_name: str
    abbr: str


class TeamStatsDict(TypedDict, total=False):
    """Team statistics. All fields optional."""

    duels_lost: float | None
    penalties_saved: float | None
    blocked_shots: float | None
    shots_on_target_incl_goals: float | None
    expected_goals_on_target: float | None
    games_played: float | None
    crossing_accuracy: float | None
    total_passes: float | None
    goals: float | None
    offsides: float | None
    away_goals: float | None
    tackle_success: float | None
    red_card_2nd_yellow: float | None
    obox_blocked: float | None
    index: float | None
    passing_accuracy: float | None
    ibox_target: float | None
    aerial_duels_lost: float | None
    goals_conceded_outside_box: float | None
    own_goals_accrued: float | None
    ground_duels_won: float | None
    successful_corners_into_box: float | None
    penalty_goals_conceded: float | None
    expected_goals_on_target_conceded: float | None
    key_passes_attempt_assists: float | None
    successful_launches: float | None
    total_fouls_won: float | None
    recoveries: float | None
    points_gained_from_losing_positions: float | None
    passing_percent_opp_half: float | None
    shots_on_conceded_inside_box: float | None
    right_foot_goals: float | None
    left_foot_goals: float | None
    unsuccessful_dribbles: float | None
    unsuccessful_crosses_and_corners: float | None
    other_goals: float | None
    times_tackled: float | None
    freekick_total: float | None
    open_play_passes: float | None
    gk_successful_distribution: float | None
    shots_off_target_incl_woodwork: float | None
    total_losses_of_possession: float | None
    tackles_won: float | None
    attempts_from_set_pieces: float | None
    total_shots_conceded: float | None
    total_fouls_conceded: float | None
    unsuccessful_corners_into_box: float | None
    successful_long_passes: float | None
    clearances_off_the_line: float | None
    throw_ins_to_own_player: float | None
    touches_in_opp_box: float | None
    hit_woodwork: float | None
    successful_passes_own_half: float | None
    points_dropped_from_winning_positions: float | None
    own_goals_conceded: float | None
    handballs_conceded: float | None
    unsuccessful_long_passes: float | None
    unsuccessful_passes_own_half: float | None
    successful_crosses_open_play: float | None
    expected_assists: float | None
    total_red_cards: float | None
    expected_goals_freekick: float | None
    catches: float | None
    overruns: float | None
    unsuccessful_passes_opposition_half: float | None
    total_shots: float | None
    unsuccessful_short_passes: float | None
    goal_assists: float | None
    successful_layoffs: float | None
    foul_won_penalty: float | None
    unsuccessful_crosses_open_play: float | None
    goal_kicks: float | None
    corners_taken_incl_short_corners: float | None
    aerial_duels: float | None
    clean_sheets: float | None
    shooting_accuracy: float | None
    successful_crosses_and_corners: float | None
    unsuccessful_layoffs: float | None
    duels_won: float | None
    penalties_conceded: float | None
    putthrough_blocked_distribution: float | None
    successful_short_passes: float | None
    throw_ins_to_opposition_player: float | None
    successful_open_play_passes: float | None
    total_clearances: float | None
    goals_conceded: float | None
    ground_duels_lost: float | None
    duels: float | None
    putthrough_blocked_distribution_won: float | None
    home_goals: float | None
    possession_percentage: float | None
    obox_target: float | None
    tackles_lost: float | None
    last_player_tackle: float | None
    successful_passes_opposition_half: float | None
    goals_conceded_inside_box: float | None
    headed_goals: float | None
    ibox_blocked: float | None
    ground_duels: float | None
    aerial_duels_won: float | None
    straight_red_cards: float | None
    corners_won: float | None
    successful_dribbles: float | None
    blocks: float | None
    gk_unsuccessful_distribution: float | None
    interceptions: float | None
    penalty_goals: float | None
    unsuccessful_launches: float | None
    foul_attempted_tackle: float | None
    shots_on_conceded_outside_box: float | None
    goal_conversion: float | None
    expected_goals: float | None
    yellow_cards: float | None


class V2TeamStatsResponse(RawResponseModel):
    """GET v2/competitions/{comp_id}/seasons/{season_id}/teams/{team_id}/stats"""

    stats: TeamStatsDict
    team: TeamSimpleDict
