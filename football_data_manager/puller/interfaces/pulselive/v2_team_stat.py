from typing import TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel


class TeamSimpleDict(TypedDict):
    """Simple team info used in statistics responses."""

    id: str
    name: str
    shortName: str
    abbr: str


class TeamStatsDict(TypedDict, total=False):
    """Team statistics. All fields optional."""

    duelsLost: float | None
    penaltiesSaved: float | None
    blockedShots: float | None
    shotsOnTargetInclGoals: float | None
    expectedGoalsOnTarget: float | None
    gamesPlayed: float | None
    crossingAccuracy: float | None
    totalPasses: float | None
    goals: float | None
    offsides: float | None
    awayGoals: float | None
    tackleSuccess: float | None
    redCard2ndYellow: float | None
    oboxBlocked: float | None
    index: float | None
    passingAccuracy: float | None
    iboxTarget: float | None
    aerialDuelsLost: float | None
    goalsConcededOutsideBox: float | None
    ownGoalsAccrued: float | None
    groundDuelsWon: float | None
    successfulCornersIntoBox: float | None
    penaltyGoalsConceded: float | None
    expectedGoalsOnTargetConceded: float | None
    keyPassesAttemptAssists: float | None
    successfulLaunches: float | None
    totalFoulsWon: float | None
    recoveries: float | None
    pointsGainedFromLosingPositions: float | None
    passingPercentOppHalf: float | None
    shotsOnConcededInsideBox: float | None
    rightFootGoals: float | None
    leftFootGoals: float | None
    unsuccessfulDribbles: float | None
    unsuccessfulCrossesAndCorners: float | None
    otherGoals: float | None
    timesTackled: float | None
    freekickTotal: float | None
    openPlayPasses: float | None
    gkSuccessfulDistribution: float | None
    shotsOffTargetInclWoodwork: float | None
    totalLossesOfPossession: float | None
    tacklesWon: float | None
    attemptsFromSetPieces: float | None
    totalShotsConceded: float | None
    totalFoulsConceded: float | None
    unsuccessfulCornersIntoBox: float | None
    successfulLongPasses: float | None
    clearancesOffTheLine: float | None
    throwInsToOwnPlayer: float | None
    touchesInOppBox: float | None
    hitWoodwork: float | None
    successfulPassesOwnHalf: float | None
    pointsDroppedFromWinningPositions: float | None
    ownGoalsConceded: float | None
    handballsConceded: float | None
    unsuccessfulLongPasses: float | None
    unsuccessfulPassesOwnHalf: float | None
    successfulCrossesOpenPlay: float | None
    expectedAssists: float | None
    totalRedCards: float | None
    expectedGoalsFreekick: float | None
    catches: float | None
    overruns: float | None
    unsuccessfulPassesOppositionHalf: float | None
    totalShots: float | None
    unsuccessfulShortPasses: float | None
    goalAssists: float | None
    successfulLayoffs: float | None
    foulWonPenalty: float | None
    unsuccessfulCrossesOpenPlay: float | None
    goalKicks: float | None
    cornersTakenInclShortCorners: float | None
    aerialDuels: float | None
    cleanSheets: float | None
    shootingAccuracy: float | None
    successfulCrossesAndCorners: float | None
    unsuccessfulLayoffs: float | None
    duelsWon: float | None
    penaltiesConceded: float | None
    putthroughBlockedDistribution: float | None
    successfulShortPasses: float | None
    throwInsToOppositionPlayer: float | None
    successfulOpenPlayPasses: float | None
    totalClearances: float | None
    goalsConceded: float | None
    groundDuelsLost: float | None
    duels: float | None
    putthroughBlockedDistributionWon: float | None
    homeGoals: float | None
    possessionPercentage: float | None
    oboxTarget: float | None
    tacklesLost: float | None
    lastPlayerTackle: float | None
    successfulPassesOppositionHalf: float | None
    goalsConcededInsideBox: float | None
    headedGoals: float | None
    iboxBlocked: float | None
    groundDuels: float | None
    aerialDuelsWon: float | None
    straightRedCards: float | None
    cornersWon: float | None
    successfulDribbles: float | None
    blocks: float | None
    gkUnsuccessfulDistribution: float | None
    interceptions: float | None
    penaltyGoals: float | None
    unsuccessfulLaunches: float | None
    foulAttemptedTackle: float | None
    shotsOnConcededOutsideBox: float | None
    goalConversion: float | None
    expectedGoals: float | None
    yellowCards: float | None


class V2TeamStatsResponse(RawResponseModel):
    """GET v2/competitions/{comp_id}/seasons/{season_id}/teams/{team_id}/stats"""

    stats: TeamStatsDict
    team: TeamSimpleDict
