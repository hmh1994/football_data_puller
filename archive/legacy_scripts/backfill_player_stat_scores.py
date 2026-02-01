# c.py
"""
Player Stat Score Update Script.

Calculates and updates 5 section scores (shooting, passing, defending, dribbling, discipline)
and an overall score for all PlayerStatEntity records in the database.

Usage:
    python c.py
"""

import math
from asyncio import run
from dataclasses import dataclass

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.player_stats.player_stat_entity import (
    PlayerStatEntity,
)
from football_data_manager.common.repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.services.common_service_container import (
    CommonServiceContainer,
)


# ============================================================
# 1. Constants
# ============================================================

# Prior strength constants
M0 = 450.0  # minutes prior strength (약 5경기)

# Shooting
NA0_SHOTS = 15.0  # shots attempts prior strength (5경기 기준)
NR0_XG = 0.75  # xG prior strength (5경기 기준)

# Passing
NP0_PASSES = 200.0  # pass attempts prior strength (5경기 기준)
NC0_CROSSES = 15.0  # cross attempts prior strength (5경기 기준)
NL0_LONG = 12.5  # long ball attempts prior strength (5경기 기준)

# Defending
ND0_DUELS = 40.0  # duels prior strength (5경기 기준)
NA0_AERIAL = 20.0  # aerial duels prior strength (5경기 기준)

# Dribbling
ND0_DRIBBLE = 20.0  # dribble attempts prior strength (5경기 기준)

# Overall score calculation constants
# ============================================================
# 문제점: 기존 설정(lam=0.5, m0=450)에서 Overall 최대 55점, 출전없는 선수 50점
# 해결책:
#   1. 기하평균 비중 축소 (lam=0.3): 한 섹션 낮아도 급락 방지
#   2. Prior 강도 축소 (m0=225): 출전시간 영향력 증가
#   3. 출전 없는 선수 0점 처리
# ============================================================
M0_OVERALL = 225.0  # Overall shrink prior strength (약 2.5경기)
LAM_OVERALL = 0.3   # 산술평균 70% + 기하평균 30% 혼합
PRIOR_OVERALL = 0.5  # Overall prior (중립값)

# Position-based weights: [shooting, passing, defending, dribbling, discipline]
POSITION_WEIGHTS = {
    PositionEnum.FORWARD: [0.35, 0.20, 0.05, 0.30, 0.10],
    PositionEnum.MIDFIELDER: [0.20, 0.35, 0.15, 0.20, 0.10],
    PositionEnum.DEFENDER: [0.05, 0.20, 0.45, 0.10, 0.20],
    PositionEnum.GOALKEEPER: [0.00, 0.10, 0.80, 0.00, 0.10],
    PositionEnum.UNKNOWN: [0.20, 0.25, 0.25, 0.15, 0.15],
}


# ============================================================
# 2. Utility Functions
# ============================================================


def clamp(x: float, lo: float, hi: float) -> float:
    """Clamp value to [lo, hi] range."""
    return min(max(x, lo), hi)


def sdiv(u: float, v: float, eps: float = 1e-9) -> float:
    """Safe division (prevent division by zero)."""
    return u / max(v, eps)


def per90(count: float, minutes: float) -> float:
    """Calculate per-90-minute rate."""
    return 90.0 * count / max(minutes, 1.0)


def shrink(x: float, prior: float, n: float, n0: float) -> float:
    """Bayesian shrinkage toward prior when sample size is small."""
    return (n * x + n0 * prior) / (n + n0)


def norm01(x: float, lo: float, hi: float) -> float:
    """Normalize [lo, hi] range to [0, 1]."""
    return clamp((x - lo) / max(hi - lo, 1e-9), 0.0, 1.0)


def score100(features: list[float], weights: list[float]) -> float:
    """Calculate weighted sum and convert to 0~100 score."""
    s = sum(w * f for w, f in zip(weights, features))
    return 100.0 * clamp(s, 0.0, 1.0)


def wmean(z: list[float], w: list[float]) -> float:
    """Weighted arithmetic mean."""
    return sum(wi * zi for wi, zi in zip(w, z))


def wgeom(z: list[float], w: list[float], eps: float = 1e-6) -> float:
    """Weighted geometric mean (enforces balance)."""
    return math.exp(sum(wi * math.log(max(zi, eps)) for wi, zi in zip(w, z)))


def blend(a: float, g: float, lam: float = 0.5) -> float:
    """Blend arithmetic and geometric means."""
    return (1.0 - lam) * a + lam * g


# ============================================================
# 3. Prior Data Class
# ============================================================


@dataclass
class SeasonPriors:
    """Prior values for a season, used for Bayesian shrinkage."""

    # Shooting priors (per90: minutes-weighted)
    npxg90_prior: float  # per90(npxG)
    npg90_prior: float  # per90(non-penalty goals)

    # Shooting priors (ratio: denominator sum)
    sot_rate_prior: float  # total_SOT / total_Shots
    goals_xg_ratio_prior: float  # total_np_goals / total_npxG (non-penalty xG)

    # Passing priors (per90: minutes-weighted)
    xa90_prior: float  # per90(xA)
    chances90_prior: float  # per90(chances_created)
    assists90_prior: float  # per90(assists)

    # Passing priors (ratio: denominator sum)
    pass_acc_prior: float  # total_pass_success / total_passes
    cross_acc_prior: float  # total_cross_success / total_crosses
    long_acc_prior: float  # total_long_success / total_long_balls

    # Defending priors (per90: minutes-weighted)
    tackles90_prior: float
    interceptions90_prior: float
    blocked90_prior: float
    recoveries90_prior: float
    fouls90_prior: float

    # Defending priors (ratio: denominator sum)
    duel_win_prior: float  # total_duels_won / total_duels
    aerial_win_prior: float  # total_aerial_won / total_aerial

    # Goalkeeping priors (per90: GK minutes-weighted)
    saves90_prior: float
    goals_prevented90_prior: float
    clean_sheets90_prior: float

    # Dribbling priors (per90: minutes-weighted)
    dribble90_prior: float
    fouls_won90_prior: float
    box_touches90_prior: float

    # Dribbling priors (ratio: denominator sum)
    dribble_rate_prior: float  # total_dribble_success / total_dribble_attempts

    # Discipline priors (per90: weighted cards)
    cards90_prior: float  # weighted cards: y + 2*(r-rd) + 3*rd

    # Overall prior (0~1 range)
    overall_prior: float


# ============================================================
# 4. Prior Calculation
# ============================================================


def calculate_season_priors(
    player_stats: list[PlayerStatEntity],
    player_position_map: dict[str, PositionEnum],
) -> SeasonPriors:
    """
    Calculate prior values for a season based on all player stats.

    :param player_stats: List of player stat entities for the season
    :param player_position_map: Mapping of player_id to PositionEnum
    :returns: SeasonPriors with calculated prior values
    """
    # Total minutes for per90 calculations
    total_minutes = sum(ps.minutes_played or 0 for ps in player_stats)
    total_minutes = max(total_minutes, 1)  # Prevent division by zero

    # =========================================
    # Shooting priors (per90)
    # =========================================
    total_npxg = sum(ps.shooting_expected_goals_non_penalty or 0 for ps in player_stats)
    npxg90_prior = 90 * total_npxg / total_minutes

    total_np_goals = sum(
        max((ps.shooting_goals or 0) - (ps.shooting_goals_penalty or 0), 0)
        for ps in player_stats
    )
    npg90_prior = 90 * total_np_goals / total_minutes

    # =========================================
    # Shooting priors (ratio)
    # =========================================
    total_sot = sum(ps.shooting_shots_on_target or 0 for ps in player_stats)
    total_shots = sum(ps.shooting_shots or 0 for ps in player_stats)
    sot_rate_prior = total_sot / max(total_shots, 1)

    total_npxg_for_ratio = sum(
        ps.shooting_expected_goals_non_penalty or 0 for ps in player_stats
    )
    goals_xg_ratio_prior = total_np_goals / max(total_npxg_for_ratio, 1e-9)

    # =========================================
    # Passing priors (per90)
    # =========================================
    total_xa = sum(ps.passing_expected_assists or 0 for ps in player_stats)
    xa90_prior = 90 * total_xa / total_minutes

    total_chances = sum(ps.passing_chances_created or 0 for ps in player_stats)
    chances90_prior = 90 * total_chances / total_minutes

    total_assists = sum(ps.passing_assists or 0 for ps in player_stats)
    assists90_prior = 90 * total_assists / total_minutes

    # =========================================
    # Passing priors (ratio)
    # =========================================
    total_pass_success = sum(ps.passing_passes_successful or 0 for ps in player_stats)
    total_passes = sum(ps.passing_passes_total or 0 for ps in player_stats)
    pass_acc_prior = total_pass_success / max(total_passes, 1)

    total_cross_success = sum(ps.passing_crosses_successful or 0 for ps in player_stats)
    total_crosses = sum(ps.passing_crosses_total or 0 for ps in player_stats)
    cross_acc_prior = total_cross_success / max(total_crosses, 1)

    total_long_success = sum(ps.passing_long_balls_accurate or 0 for ps in player_stats)
    total_long_balls = sum(ps.passing_long_balls_total or 0 for ps in player_stats)
    long_acc_prior = total_long_success / max(total_long_balls, 1)

    # =========================================
    # Defending priors (per90)
    # =========================================
    total_tackles = sum(ps.defending_tackles_won or 0 for ps in player_stats)
    tackles90_prior = 90 * total_tackles / total_minutes

    total_interceptions = sum(ps.defending_interceptions or 0 for ps in player_stats)
    interceptions90_prior = 90 * total_interceptions / total_minutes

    total_blocked = sum(ps.defending_blocked or 0 for ps in player_stats)
    blocked90_prior = 90 * total_blocked / total_minutes

    total_recoveries = sum(ps.defending_recoveries or 0 for ps in player_stats)
    recoveries90_prior = 90 * total_recoveries / total_minutes

    total_fouls = sum(ps.defending_fouls_committed or 0 for ps in player_stats)
    fouls90_prior = 90 * total_fouls / total_minutes

    # =========================================
    # Defending priors (ratio)
    # =========================================
    total_duels_won = sum(ps.defending_duels_won or 0 for ps in player_stats)
    total_duels = sum(ps.defending_duels_total or 0 for ps in player_stats)
    duel_win_prior = total_duels_won / max(total_duels, 1)

    total_aerial_won = sum(ps.defending_duels_aerial_won or 0 for ps in player_stats)
    total_aerial = sum(ps.defending_duels_aerial_total or 0 for ps in player_stats)
    aerial_win_prior = total_aerial_won / max(total_aerial, 1)

    # =========================================
    # GK priors (per90, GK only)
    # =========================================
    gk_player_ids = {
        pid for pid, pos in player_position_map.items() if pos == PositionEnum.GOALKEEPER
    }
    gk_stats = [ps for ps in player_stats if ps.player_id in gk_player_ids]

    total_gk_minutes = sum(ps.minutes_played or 0 for ps in gk_stats)
    total_gk_minutes = max(total_gk_minutes, 1)

    total_saves = sum(ps.goalkeeping_saves or 0 for ps in gk_stats)
    saves90_prior = 90 * total_saves / total_gk_minutes

    total_prevented = sum(ps.goalkeeping_goals_prevented or 0 for ps in gk_stats)
    goals_prevented90_prior = 90 * total_prevented / total_gk_minutes

    total_cs = sum(ps.goalkeeping_clean_sheets or 0 for ps in gk_stats)
    clean_sheets90_prior = 90 * total_cs / total_gk_minutes

    # =========================================
    # Dribbling priors (per90)
    # =========================================
    total_dribble = sum(ps.possession_dribble_total or 0 for ps in player_stats)
    dribble90_prior = 90 * total_dribble / total_minutes

    total_fouls_won = sum(ps.possession_fouls_won or 0 for ps in player_stats)
    fouls_won90_prior = 90 * total_fouls_won / total_minutes

    total_box_touches = sum(
        ps.possession_touches_in_opposition_box or 0 for ps in player_stats
    )
    box_touches90_prior = 90 * total_box_touches / total_minutes

    # =========================================
    # Dribbling priors (ratio)
    # =========================================
    total_dribble_success = sum(
        ps.possession_dribble_successful or 0 for ps in player_stats
    )
    total_dribble_attempts = sum(ps.possession_dribble_total or 0 for ps in player_stats)
    dribble_rate_prior = total_dribble_success / max(total_dribble_attempts, 1)

    # =========================================
    # Discipline priors (per90, weighted cards)
    # =========================================
    total_weighted_cards = sum(
        (ps.discipline_yellow_cards or 0)
        + 2.0
        * max(
            (ps.discipline_red_cards or 0) - (ps.discipline_red_cards_direct or 0), 0.0
        )
        + 3.0 * (ps.discipline_red_cards_direct or 0)
        for ps in player_stats
    )
    cards90_prior = 90 * total_weighted_cards / total_minutes

    # =========================================
    # Overall prior (fixed neutral value)
    # =========================================
    overall_prior = 0.5

    return SeasonPriors(
        npxg90_prior=npxg90_prior,
        npg90_prior=npg90_prior,
        sot_rate_prior=sot_rate_prior,
        goals_xg_ratio_prior=goals_xg_ratio_prior,
        xa90_prior=xa90_prior,
        chances90_prior=chances90_prior,
        assists90_prior=assists90_prior,
        pass_acc_prior=pass_acc_prior,
        cross_acc_prior=cross_acc_prior,
        long_acc_prior=long_acc_prior,
        tackles90_prior=tackles90_prior,
        interceptions90_prior=interceptions90_prior,
        blocked90_prior=blocked90_prior,
        recoveries90_prior=recoveries90_prior,
        fouls90_prior=fouls90_prior,
        duel_win_prior=duel_win_prior,
        aerial_win_prior=aerial_win_prior,
        saves90_prior=saves90_prior,
        goals_prevented90_prior=goals_prevented90_prior,
        clean_sheets90_prior=clean_sheets90_prior,
        dribble90_prior=dribble90_prior,
        fouls_won90_prior=fouls_won90_prior,
        box_touches90_prior=box_touches90_prior,
        dribble_rate_prior=dribble_rate_prior,
        cards90_prior=cards90_prior,
        overall_prior=overall_prior,
    )


# ============================================================
# 5. Section Score Calculation Functions
# ============================================================


def calculate_shooting_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    """
    Calculate shooting score (0~100).

    슈팅 점수 계산식:
    ─────────────────────────────────────────────────────────────
    f1 (40%): npxG90 - 위협도
       - shrink(per90(npxG), npxg90_prior, minutes, 450)
       - norm01(값, 0.0, 0.60)

    f2 (30%): non-penalty goals 90 - 실제 득점력
       - shrink(per90(np_goals), npg90_prior, minutes, 450)
       - norm01(값, 0.0, 0.60)

    f3 (20%): SOT/Shots - 슈팅 정확도
       - shrink(sot/shots, sot_rate_prior, shots, 15)
       - norm01(값, 0.20, 0.60)

    f4 (10%): goals/xG - 결정력 (xG 대비 득점 효율)
       - shrink(np_goals/npxG, goals_xg_ratio_prior, npxG, 0.75)
       - norm01(값, 0.60, 1.40)

    최종: score = 100 × (0.40×f1 + 0.30×f2 + 0.20×f3 + 0.10×f4)
    ─────────────────────────────────────────────────────────────
    """
    m = float(ps.minutes_played or 0)
    if m < 1:
        return 0.0

    g = float(ps.shooting_goals or 0)
    g_pen = float(ps.shooting_goals_penalty or 0)
    g_np = max(g - g_pen, 0.0)

    xg_np = float(ps.shooting_expected_goals_non_penalty or 0)
    shots = float(ps.shooting_shots or 0)
    sot = float(ps.shooting_shots_on_target or 0)

    f1 = norm01(shrink(per90(xg_np, m), priors.npxg90_prior, m, M0), 0.0, 0.60)
    f2 = norm01(shrink(per90(g_np, m), priors.npg90_prior, m, M0), 0.0, 0.60)
    f3 = norm01(
        shrink(sdiv(sot, shots), priors.sot_rate_prior, shots, NA0_SHOTS), 0.20, 0.60
    )
    f4 = norm01(
        shrink(sdiv(g_np, xg_np), priors.goals_xg_ratio_prior, xg_np, NR0_XG), 0.60, 1.40
    )

    return score100([f1, f2, f3, f4], [0.40, 0.30, 0.20, 0.10])


def calculate_passing_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    """
    Calculate passing score (0~100).

    패스 점수 계산식:
    ─────────────────────────────────────────────────────────────
    f1 (30%): xA90 - 창의성 (기대 어시스트)
       - shrink(per90(xA), xa90_prior, minutes, 450)
       - norm01(값, 0.0, 0.45)

    f2 (20%): chances90 - 찬스 생성
       - shrink(per90(chances_created), chances90_prior, minutes, 450)
       - norm01(값, 0.0, 3.0)

    f3 (15%): assists90 - 어시스트
       - shrink(per90(assists), assists90_prior, minutes, 450)
       - norm01(값, 0.0, 0.35)

    f4 (25%): pass accuracy - 패스 정확도
       - shrink(success/total, pass_acc_prior, total_passes, 200)
       - norm01(값, 0.70, 0.93)

    f5 (10%): 특수 패스 정확도 (크로스 50% + 롱볼 50%)
       - 크로스: shrink(cs/ct, cross_acc_prior, ct, 15), norm01(값, 0.10, 0.35)
       - 롱볼: shrink(ls/lt, long_acc_prior, lt, 12.5), norm01(값, 0.30, 0.70)

    최종: score = 100 × (0.30×f1 + 0.20×f2 + 0.15×f3 + 0.25×f4 + 0.10×f5)
    ─────────────────────────────────────────────────────────────
    """
    m = float(ps.minutes_played or 0)
    if m < 1:
        return 0.0

    assists = float(ps.passing_assists or 0)
    chances = float(ps.passing_chances_created or 0)
    xa = float(ps.passing_expected_assists or 0)

    pt = float(ps.passing_passes_total or 0)
    psucc = float(ps.passing_passes_successful or 0)
    ct = float(ps.passing_crosses_total or 0)
    cs = float(ps.passing_crosses_successful or 0)
    lt = float(ps.passing_long_balls_total or 0)
    ls = float(ps.passing_long_balls_accurate or 0)

    f1 = norm01(shrink(per90(xa, m), priors.xa90_prior, m, M0), 0.0, 0.45)
    f2 = norm01(shrink(per90(chances, m), priors.chances90_prior, m, M0), 0.0, 3.0)
    f3 = norm01(shrink(per90(assists, m), priors.assists90_prior, m, M0), 0.0, 0.35)

    pass_acc = sdiv(psucc, pt)
    cross_acc = sdiv(cs, ct)
    long_acc = sdiv(ls, lt)

    f4 = norm01(shrink(pass_acc, priors.pass_acc_prior, pt, NP0_PASSES), 0.70, 0.93)
    f5 = 0.5 * norm01(
        shrink(cross_acc, priors.cross_acc_prior, ct, NC0_CROSSES), 0.10, 0.35
    ) + 0.5 * norm01(shrink(long_acc, priors.long_acc_prior, lt, NL0_LONG), 0.30, 0.70)

    return score100([f1, f2, f3, f4, f5], [0.30, 0.20, 0.15, 0.25, 0.10])


def calculate_defending_score_outfield(
    ps: PlayerStatEntity, priors: SeasonPriors
) -> float:
    """
    Calculate outfield player defending score (0~100).

    필드 플레이어 수비 점수 계산식:
    ─────────────────────────────────────────────────────────────
    ft (22%): tackles won 90 - 태클 성공
       - shrink(per90(tackles_won), tackles90_prior, minutes, 450)
       - norm01(값, 0.0, 3.0)

    fi (18%): interceptions 90 - 인터셉트
       - shrink(per90(interceptions), interceptions90_prior, minutes, 450)
       - norm01(값, 0.0, 2.5)

    fb (12%): blocked 90 - 블로킹
       - shrink(per90(blocked), blocked90_prior, minutes, 450)
       - norm01(값, 0.0, 1.8)

    fr (18%): recoveries 90 - 볼 회수
       - shrink(per90(recoveries), recoveries90_prior, minutes, 450)
       - norm01(값, 0.0, 8.0)

    fd (20%): duel win rate - 듀얼 승률
       - shrink(won/total, duel_win_prior, total_duels, 40)
       - norm01(값, 0.40, 0.70)

    fa (10%): aerial win rate - 공중볼 승률
       - shrink(won/total, aerial_win_prior, total_aerial, 20)
       - norm01(값, 0.40, 0.75)

    ff (-10%): fouls 90 - 파울 (감점)
       - shrink(per90(fouls), fouls90_prior, minutes, 450)
       - norm01(값, 0.0, 2.5)

    최종: score = 100 × clamp(0.22×ft + 0.18×fi + 0.12×fb + 0.18×fr + 0.20×fd + 0.10×fa - 0.10×ff, 0, 1)
    ─────────────────────────────────────────────────────────────
    """
    m = float(ps.minutes_played or 0)
    if m < 1:
        return 0.0

    tw = float(ps.defending_tackles_won or 0)
    inter = float(ps.defending_interceptions or 0)
    blk = float(ps.defending_blocked or 0)
    rec = float(ps.defending_recoveries or 0)

    dt = float(ps.defending_duels_total or 0)
    dw = float(ps.defending_duels_won or 0)
    at = float(ps.defending_duels_aerial_total or 0)
    aw = float(ps.defending_duels_aerial_won or 0)

    fouls = float(ps.defending_fouls_committed or 0)

    ft = norm01(shrink(per90(tw, m), priors.tackles90_prior, m, M0), 0.0, 3.0)
    fi = norm01(shrink(per90(inter, m), priors.interceptions90_prior, m, M0), 0.0, 2.5)
    fb = norm01(shrink(per90(blk, m), priors.blocked90_prior, m, M0), 0.0, 1.8)
    fr = norm01(shrink(per90(rec, m), priors.recoveries90_prior, m, M0), 0.0, 8.0)

    duel_win = sdiv(dw, dt)
    aerial_win = sdiv(aw, at)
    fd = norm01(shrink(duel_win, priors.duel_win_prior, dt, ND0_DUELS), 0.40, 0.70)
    fa = norm01(shrink(aerial_win, priors.aerial_win_prior, at, NA0_AERIAL), 0.40, 0.75)

    ff = norm01(shrink(per90(fouls, m), priors.fouls90_prior, m, M0), 0.0, 2.5)

    s = 0.22 * ft + 0.18 * fi + 0.12 * fb + 0.18 * fr + 0.20 * fd + 0.10 * fa - 0.10 * ff
    return 100.0 * clamp(s, 0.0, 1.0)


def calculate_defending_score_goalkeeper(
    ps: PlayerStatEntity, priors: SeasonPriors
) -> float:
    """
    Calculate goalkeeper defending score (0~100).

    골키퍼 수비 점수 계산식:
    ─────────────────────────────────────────────────────────────
    f1 (55%): saves 90 - 선방 횟수
       - shrink(per90(saves), saves90_prior, minutes, 450)
       - norm01(값, 0.0, 5.5)

    f2 (25%): goals prevented 90 - 실점 방지 (xG 대비)
       - shrink(per90(goals_prevented), goals_prevented90_prior, minutes, 450)
       - norm01(값, -0.3, 0.6)
       - 음수 가능 (xG보다 많이 실점)

    f3 (20%): clean sheets 90 - 클린시트
       - shrink(per90(clean_sheets), clean_sheets90_prior, minutes, 450)
       - norm01(값, 0.0, 0.50)

    최종: score = 100 × (0.55×f1 + 0.25×f2 + 0.20×f3)
    ─────────────────────────────────────────────────────────────
    """
    m = float(ps.minutes_played or 0)
    if m < 1:
        return 0.0

    saves = float(ps.goalkeeping_saves or 0)
    prevented = float(ps.goalkeeping_goals_prevented or 0)
    cs = float(ps.goalkeeping_clean_sheets or 0)

    f1 = norm01(shrink(per90(saves, m), priors.saves90_prior, m, M0), 0.0, 5.5)
    f2 = norm01(
        shrink(per90(prevented, m), priors.goals_prevented90_prior, m, M0), -0.3, 0.6
    )
    f3 = norm01(shrink(per90(cs, m), priors.clean_sheets90_prior, m, M0), 0.0, 0.50)

    return score100([f1, f2, f3], [0.55, 0.25, 0.20])


def calculate_dribbling_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    """
    드리블 점수 계산식:
    ─────────────────────────────────────────────────────────────
    1. 드리블 성공률 (fs) - 가중치 0.35
       - succ_rate = 성공 / 시도
       - fs = norm01(shrink(succ_rate, prior, 시도횟수, ND0_DRIBBLE), 0.35, 0.75)
       - 정규화 범위: 35%~75%

    2. 드리블 볼륨 (fv) - 가중치 0.30
       - dribble90 = shrink(per90(시도횟수), prior, minutes, M0)
       - fv = norm01(dribble90, 0.0, 7.0)
       - 정규화 범위: 0~7회/90분

    3. 파울 유도 (fw) - 가중치 0.20
       - fouls_won90 = shrink(per90(fouls_won), prior, minutes, M0)
       - fw = norm01(fouls_won90, 0.0, 2.5)
       - 정규화 범위: 0~2.5회/90분

    4. 박스 터치 (fb) - 가중치 0.15
       - box90 = shrink(per90(box_touches), prior, minutes, M0)
       - fb = norm01(box90, 0.0, 6.0)
       - 정규화 범위: 0~6회/90분

    5. 최종 점수:
       score = 100 × (0.35×fs + 0.30×fv + 0.20×fw + 0.15×fb)

    ※ 출전 없으면 0점
    """
    m = float(ps.minutes_played or 0)
    if m < 1:
        return 0.0

    dt = float(ps.possession_dribble_total or 0)
    ds = float(ps.possession_dribble_successful or 0)
    fw = float(ps.possession_fouls_won or 0)
    box = float(ps.possession_touches_in_opposition_box or 0)

    succ_rate = sdiv(ds, dt)
    fs = norm01(shrink(succ_rate, priors.dribble_rate_prior, dt, ND0_DRIBBLE), 0.35, 0.75)
    fv = norm01(shrink(per90(dt, m), priors.dribble90_prior, m, M0), 0.0, 7.0)
    fw_ = norm01(shrink(per90(fw, m), priors.fouls_won90_prior, m, M0), 0.0, 2.5)
    fb = norm01(shrink(per90(box, m), priors.box_touches90_prior, m, M0), 0.0, 6.0)

    return score100([fs, fv, fw_, fb], [0.35, 0.30, 0.20, 0.15])


def calculate_discipline_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    """
    Calculate discipline score (0~100).

    규율 점수 계산식:
    ─────────────────────────────────────────────────────────────
    1. 가중 카드 계산: c = 옐로우×1 + 간접퇴장×2 + 직접퇴장×3
    2. cards90 = shrink(per90(c), cards90_prior, minutes, M0)
    3. fouls90 = shrink(per90(fouls), fouls90_prior, minutes, M0)
    4. penalty = 0.7 × norm01(cards90, 0, 1.2) + 0.3 × norm01(fouls90, 0, 3.0)
    5. score = 100 × (1 - penalty)

    ※ 출전 없으면 0점 (데이터 없음 = 평가 불가)
    ─────────────────────────────────────────────────────────────
    """
    m = float(ps.minutes_played or 0)
    if m < 1:
        return 0.0  # 출전 없으면 0점 (기존 100점 → 0점 변경)

    y = float(ps.discipline_yellow_cards or 0)
    r = float(ps.discipline_red_cards or 0)
    rd = float(ps.discipline_red_cards_direct or 0)
    fouls = float(ps.defending_fouls_committed or 0)

    # 가중 카드 페널티: 경고 1, 간접퇴장 2, 직접퇴장 3
    c = y + 2.0 * max(r - rd, 0.0) + 3.0 * rd

    c90 = shrink(per90(c, m), priors.cards90_prior, m, M0)
    f90 = shrink(per90(fouls, m), priors.fouls90_prior, m, M0)

    p = 0.7 * norm01(c90, 0.0, 1.2) + 0.3 * norm01(f90, 0.0, 3.0)
    return 100.0 * (1.0 - clamp(p, 0.0, 1.0))


# ============================================================
# 6. Overall Score Calculation
# ============================================================


def calculate_overall_score(
    s_shot: float,
    s_pass: float,
    s_def: float,
    s_drb: float,
    s_disc: float,
    minutes: float,
    position: PositionEnum,
    prior_overall: float = PRIOR_OVERALL,
    m0: float = M0_OVERALL,
    lam: float = LAM_OVERALL,
) -> float:
    """
    Calculate overall score (0~100) from 5 section scores.

    Overall 점수 계산식:
    ─────────────────────────────────────────────────────────────
    1. 섹션 점수 정규화: z[i] = section_score[i] / 100

    2. 포지션별 가중치 적용:
       - FW: [슈팅 0.35, 패스 0.20, 수비 0.05, 드리블 0.30, 규율 0.10]
       - MF: [슈팅 0.20, 패스 0.35, 수비 0.15, 드리블 0.20, 규율 0.10]
       - DF: [슈팅 0.05, 패스 0.20, 수비 0.45, 드리블 0.10, 규율 0.20]
       - GK: [슈팅 0.00, 패스 0.10, 수비 0.80, 드리블 0.00, 규율 0.10]

    3. 가중 평균 계산:
       - 산술평균: a = Σ(w[i] × z[i])
       - 기하평균: g = exp(Σ(w[i] × log(z[i])))

    4. 혼합 (lam=0.3):
       - r = (1-lam) × a + lam × g
       - 산술평균 70% + 기하평균 30%
       - 기하평균 비중 축소로 한 섹션 낮아도 급락 방지

    5. 출전시간 Shrink (m0=225분 ≈ 2.5경기):
       - r_shrunk = (minutes × r + m0 × prior) / (minutes + m0)
       - prior = 0.5 (중립값)
       - 출전시간 적을수록 0.5로 수렴

    6. 최종 점수: score = 100 × clamp(r_shrunk, 0, 1)

    ※ 출전 없으면 0점 (데이터 없음 = 평가 불가)
    ─────────────────────────────────────────────────────────────

    :param s_shot: Shooting score (0~100)
    :param s_pass: Passing score (0~100)
    :param s_def: Defending score (0~100)
    :param s_drb: Dribbling score (0~100)
    :param s_disc: Discipline score (0~100)
    :param minutes: Minutes played
    :param position: Player position (PositionEnum)
    :param prior_overall: Prior value for overall (default: 0.5)
    :param m0: Prior strength in minutes (default: 225)
    :param lam: Blend ratio for arithmetic/geometric mean (default: 0.3)
    :returns: Overall score (0~100)
    """
    # 출전 없으면 0점 (기존: 50점으로 계산됨)
    if minutes < 1:
        return 0.0

    weights = POSITION_WEIGHTS.get(position, POSITION_WEIGHTS[PositionEnum.UNKNOWN])

    # 섹션 점수를 0~1로 정규화
    z = [s_shot / 100.0, s_pass / 100.0, s_def / 100.0, s_drb / 100.0, s_disc / 100.0]

    # 가중 산술평균 + 가중 기하평균 혼합
    # lam=0.3: 산술평균 70% + 기하평균 30%
    a = wmean(z, weights)
    g = wgeom(z, weights)
    r = blend(a, g, lam=lam)

    # 출전시간 기반 shrink (m0=225분 ≈ 2.5경기)
    # 출전시간 적으면 prior(0.5)로 수렴, 많으면 실제 성적 반영
    r_shrunk = shrink(r, prior_overall, minutes, m0)
    return 100.0 * clamp(r_shrunk, 0.0, 1.0)


# ============================================================
# 7. Main Update Function
# ============================================================


async def update_player_stat_scores(
    repository_container: CommonRepositoryContainer,
) -> list[PlayerStatEntity]:
    """
    Calculate and update score fields for all PlayerStatEntity in each season.

    :param repository_container: Repository container for database operations
    :returns: List of updated player stat entities
    """
    print("=" * 80)
    print("Player Stat Score Update Process")
    print("=" * 80)

    # Initialize repositories
    competition_repository = repository_container.competition_repository()
    season_repository = repository_container.season_repository()
    player_stat_repository = repository_container.player_stat_repository()
    player_repository = repository_container.player_repository()

    # Get competition (Pulselive ID = 8)
    competition = await competition_repository.read_by_pulselive_id(8)
    if not competition:
        print("Error: Competition not found")
        return []

    # Get seasons sorted from oldest to newest
    seasons = await season_repository.read_by_competition(competition)
    if not seasons:
        print("Error: No seasons found")
        return []

    seasons.sort(key=lambda s: s.year_start)

    all_updated_player_stats = []

    for season in seasons:
        print(f"\nProcessing season {season.year_start}...")

        # Step 1: Get all player stats for the season
        player_stats = await player_stat_repository.read_by_season(season)
        if not player_stats:
            print(f"  No player stats found for season {season.year_start}")
            continue

        print(f"  Found {len(player_stats)} player stats")

        # Step 2: Build player position cache (needed for GK Prior calculation)
        player_ids = list(set(ps.player_id for ps in player_stats if ps.player_id))
        players = await player_repository.read_by_ids(player_ids)
        player_position_map = {p.id: p.position for p in players}

        # Step 3: Calculate priors for the season
        priors = calculate_season_priors(player_stats, player_position_map)
        print("  Priors calculated")

        # Step 4: Calculate scores for each player stat
        updated_count = 0
        for ps in player_stats:
            # Get player position from PlayerEntity
            position = player_position_map.get(ps.player_id, PositionEnum.UNKNOWN)
            is_goalkeeper = position == PositionEnum.GOALKEEPER

            # Calculate section scores
            ps.score_shooting = calculate_shooting_score(ps, priors)
            ps.score_passing = calculate_passing_score(ps, priors)

            if is_goalkeeper:
                ps.score_defending = calculate_defending_score_goalkeeper(ps, priors)
            else:
                ps.score_defending = calculate_defending_score_outfield(ps, priors)

            ps.score_dribbling = calculate_dribbling_score(ps, priors)
            ps.score_discipline = calculate_discipline_score(ps, priors)

            # Calculate overall score
            ps.score_overall = calculate_overall_score(
                ps.score_shooting,
                ps.score_passing,
                ps.score_defending,
                ps.score_dribbling,
                ps.score_discipline,
                float(ps.minutes_played or 0),
                position,
                priors.overall_prior,
            )

            # Update in database
            await player_stat_repository.update(ps)
            all_updated_player_stats.append(ps)
            updated_count += 1

        print(f"  Updated {updated_count} player stats for season {season.year_start}")

    print(f"\n{'=' * 80}")
    print(f"Total updated: {len(all_updated_player_stats)} player stat entities")
    print("=" * 80)

    return all_updated_player_stats


# ============================================================
# 8. Entry Point
# ============================================================


async def main():
    """Main entry point for the script."""
    service_container = CommonServiceContainer()
    service_container.container_config.from_dict({"config_path": "./configs/.env"})
    db_service = service_container.db_service()

    async with db_service.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repository_container = CommonRepositoryContainer(db_service=db_service)

    await update_player_stat_scores(repository_container)


if __name__ == "__main__":
    run(main())
