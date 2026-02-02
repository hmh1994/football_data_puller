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
    blockedShots: float | None
    aerialDuels: float | None
    aerialDuelsWon: float | None
    groundDuels: float | None
    groundDuelsWon: float | None
    duels: float | None
    duelsWon: float | None
    totalFoulsConceded: float | None
    interceptions: float | None
    possessionWonFinalThird: float | None
    recoveries: float | None
    totalTackles: float | None
    tacklesWon: float | None
    totalRedCards: float | None
    straightRedCards: float | None
    yellowCards: float | None
    cleanSheets: float | None
    goalsConceded: float | None
    expectedGoalsOnTargetConceded: float | None
    catches: float | None
    penaltiesFaced: float | None
    penaltyGoalsConceded: float | None
    savesMade: float | None
    successfulLongPasses: float | None
    unsuccessfulLongPasses: float | None
    goalAssists: float | None
    keyPassesAttemptAssists: float | None
    expectedAssists: float | None
    successfulShortPasses: float | None
    totalPasses: float | None
    successfulCrossesAndCorners: float | None
    unsuccessfulCrossesAndCorners: float | None
    successfulDribbles: float | None
    unsuccessfulDribbles: float | None
    totalFoulsWon: float | None
    touches: float | None
    totalTouchesInOppositionBox: float | None
    expectedGoals: float | None
    penaltiesTaken: float | None
    expectedGoalsOnTarget: float | None
    goals: float | None
    penaltyGoals: float | None
    totalShots: float | None
    shotsOnTargetIncGoals: float | None


class V2PlayerStatResponse(RawResponseModel):
    """GET v2/competitions/{comp_id}/seasons/{season_id}/players/{player_id}/stats"""

    player: PlayerResponse
    stats: PlayerStatsDict
