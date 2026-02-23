from typing import TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive.v1_player import (
    PlayerDetailResponse,
    PlayerResponse,
)


# --- v2/.../squad ---


class V2SquadResponse(RawResponseModel):
    """GET v2/competitions/{comp_id}/seasons/{season_id}/teams/{team_id}/squad"""

    players: list[PlayerDetailResponse]


# --- v2/.../players/{id}/stats ---


class PlayerStatsDict(TypedDict, total=False):
    """Player statistics. All fields optional."""

    appearances: float | None
    blocked_shots: float | None
    aerial_duels: float | None
    aerial_duels_won: float | None
    ground_duels: float | None
    ground_duels_won: float | None
    duels: float | None
    duels_won: float | None
    total_fouls_conceded: float | None
    interceptions: float | None
    possession_won_final_third: float | None
    recoveries: float | None
    total_tackles: float | None
    tackles_won: float | None
    total_red_cards: float | None
    straight_red_cards: float | None
    yellow_cards: float | None
    clean_sheets: float | None
    goals_conceded: float | None
    expected_goals_on_target_conceded: float | None
    catches: float | None
    penalties_faced: float | None
    penalty_goals_conceded: float | None
    saves_made: float | None
    successful_long_passes: float | None
    unsuccessful_long_passes: float | None
    goal_assists: float | None
    key_passes_attempt_assists: float | None
    expected_assists: float | None
    successful_short_passes: float | None
    total_passes: float | None
    successful_crosses_and_corners: float | None
    unsuccessful_crosses_and_corners: float | None
    successful_dribbles: float | None
    unsuccessful_dribbles: float | None
    total_fouls_won: float | None
    touches: float | None
    total_touches_in_opposition_box: float | None
    expected_goals: float | None
    penalties_taken: float | None
    expected_goals_on_target: float | None
    goals: float | None
    penalty_goals: float | None
    total_shots: float | None
    shots_on_target_inc_goals: float | None


class V2PlayerStatResponse(RawResponseModel):
    """GET v2/competitions/{comp_id}/seasons/{season_id}/players/{player_id}/stats"""

    player: PlayerResponse
    stats: PlayerStatsDict
