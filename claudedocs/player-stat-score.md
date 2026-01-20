# Player Stat Score Update 구현 계획

## 1. 개요

본 문서는 `claudedocs/player-stat-score-chat.md`에서 정의한 5개 섹션 점수(슈팅/패스/수비/드리블/규율)와 Overall 점수를 `PlayerStatEntity`에 업데이트하기 위한
구현 계획을 정의합니다.

### 1.1 기존 구조 확인

`PlayerStatEntity`에는 이미 다음 점수 필드가 정의되어 있습니다:

- `score_shooting` (Double, default=0.0)
- `score_passing` (Double, default=0.0)
- `score_defending` (Double, default=0.0)
- `score_dribbling` (Double, default=0.0)
- `score_discipline` (Double, default=0.0)
- `score_overall` (Double, default=0.0)
- `minutes_played` (Integer, nullable) - 이미 구현됨

### 1.2 Prior 정의 방식

**결정사항**: Prior 값은 지표 유형에 따라 다른 방식으로 산출합니다.

| 지표 유형        | 계산 방식            | 예시                              |
|--------------|------------------|---------------------------------|
| **per90 지표** | 출전시간 가중 평균       | npxG90, assists90, tackles90 등  |
| **비율 지표**    | 분모 합 기준 비율       | SOT/Shots, pass_acc, duel_win 등 |
| **GK 지표**    | 출전시간 가중 평균 (GK만) | saves90, clean_sheets90 등       |

---

## 2. 구현 흐름

```
[시즌 순회] → [Prior 계산 (시즌별)] → [PlayerStat 순회] → [5개 섹션 점수 계산] → [Overall 점수 계산] → [DB 업데이트]
```

### 2.1 실행 진입점

`c.py`에서 `python c.py`로 실행:

```python
async def update_player_stat_scores(
        repository_container: CommonRepositoryContainer,
) -> list[PlayerStatEntity]:
    """
    Calculate and update score fields for all PlayerStatEntity in each season.
    """
```

---

## 3. Prior 계산을 위한 Repository 구현

### 3.1 필요한 신규 메서드

`PlayerStatRepository`에 추가할 메서드:

#### 3.1.1 `read_by_season`

시즌별 모든 PlayerStat을 조회합니다.

```python
@PulseliveRepository.with_db_session
async def read_by_season(
        self,
        session: AsyncSession,
        season: SeasonEntity,
) -> list[PlayerStatEntity]:
    """
    Get all player stat entities for a specific season.

    :param session: Database session
    :param season: Season entity
    :returns: List of player stat entities for the season
    """
    stmt = select(PlayerStatEntity).where(
        PlayerStatEntity.season_id == season.id,
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())
```

### 3.2 Prior 계산 함수

`c.py`에 정의:

```python
@dataclass
class SeasonPriors:
    """해당 시즌의 Prior 값들을 저장하는 데이터 클래스"""

    # Shooting priors (per90: 출전시간 가중)
    npxg90_prior: float  # per90(npxG)
    npg90_prior: float  # per90(non-penalty goals)

    # Shooting priors (비율: 분모 합 기준)
    sot_rate_prior: float  # total_SOT / total_Shots
    goals_xg_ratio_prior: float  # total_np_goals / total_npxG (분모: non-penalty xG)

    # Passing priors (per90: 출전시간 가중)
    xa90_prior: float  # per90(xA)
    chances90_prior: float  # per90(chances_created)
    assists90_prior: float  # per90(assists)

    # Passing priors (비율: 분모 합 기준)
    pass_acc_prior: float  # total_pass_success / total_passes
    cross_acc_prior: float  # total_cross_success / total_crosses
    long_acc_prior: float  # total_long_success / total_long_balls

    # Defending priors (per90: 출전시간 가중)
    tackles90_prior: float
    interceptions90_prior: float
    blocked90_prior: float
    recoveries90_prior: float
    fouls90_prior: float

    # Defending priors (비율: 분모 합 기준)
    duel_win_prior: float  # total_duels_won / total_duels
    aerial_win_prior: float  # total_aerial_won / total_aerial

    # Goalkeeping priors (per90: GK 출전시간 가중)
    saves90_prior: float
    goals_prevented90_prior: float
    clean_sheets90_prior: float

    # Dribbling priors (per90: 출전시간 가중)
    dribble90_prior: float
    fouls_won90_prior: float
    box_touches90_prior: float

    # Dribbling priors (비율: 분모 합 기준)
    dribble_rate_prior: float  # total_dribble_success / total_dribble_attempts

    # Discipline priors (per90: 가중 카드)
    cards90_prior: float  # 가중 카드: y + 2*(r-rd) + 3*rd

    # Overall prior (0~1 범위)
    overall_prior: float
```

### 3.3 Prior 계산식 상세

#### 3.3.1 per90 지표 (출전시간 가중 평균)

```python
# 예시: npxg90_prior 계산
total_npxg = sum(ps.shooting_expected_goals_non_penalty or 0 for ps in player_stats)
total_minutes = sum(ps.minutes_played or 0 for ps in player_stats)
npxg90_prior = 90 * total_npxg / max(total_minutes, 1)

# 동일 방식 적용 지표:
# - npg90_prior, xa90_prior, chances90_prior, assists90_prior
# - tackles90_prior, interceptions90_prior, blocked90_prior, recoveries90_prior, fouls90_prior
# - dribble90_prior, fouls_won90_prior, box_touches90_prior

# cards90_prior 계산 (가중 카드: 옐로우 1, 간접퇴장 2, 직접퇴장 3)
# 규율 점수 계산과 동일한 가중치 적용
total_weighted_cards = sum(
    (ps.discipline_yellow_cards or 0)
    + 2.0 * max((ps.discipline_red_cards or 0) - (ps.discipline_red_cards_direct or 0), 0.0)
    + 3.0 * (ps.discipline_red_cards_direct or 0)
    for ps in player_stats
)
cards90_prior = 90 * total_weighted_cards / max(total_minutes, 1)
```

#### 3.3.2 비율 지표 (분모 합 기준 비율)

```python
# 예시: sot_rate_prior 계산 (SOT/Shots)
total_sot = sum(ps.shooting_shots_on_target or 0 for ps in player_stats)
total_shots = sum(ps.shooting_shots or 0 for ps in player_stats)
sot_rate_prior = total_sot / max(total_shots, 1)

# 예시: pass_acc_prior 계산
total_pass_success = sum(ps.passing_passes_successful or 0 for ps in player_stats)
total_passes = sum(ps.passing_passes_total or 0 for ps in player_stats)
pass_acc_prior = total_pass_success / max(total_passes, 1)

# 예시: duel_win_prior 계산
total_duels_won = sum(ps.defending_duels_won or 0 for ps in player_stats)
total_duels = sum(ps.defending_duels_total or 0 for ps in player_stats)
duel_win_prior = total_duels_won / max(total_duels, 1)

# 동일 방식 적용 지표:
# - goals_xg_ratio_prior: total_np_goals / total_npxG (분모: non-penalty xG)
# - cross_acc_prior: total_cross_success / total_crosses
# - long_acc_prior: total_long_success / total_long_balls
# - aerial_win_prior: total_aerial_won / total_aerial
# - dribble_rate_prior: total_dribble_success / total_dribble_attempts
```

#### 3.3.3 GK 지표 (GK 출전시간 가중)

```python
# GK만 필터링 (PositionEnum.GOALKEEPER)
# player_position_map: dict[int, PositionEnum] - 미리 계산된 player_id → position 매핑
gk_player_ids = {pid for pid, pos in player_position_map.items() if pos == PositionEnum.GOALKEEPER}
gk_stats = [ps for ps in player_stats if ps.player_id in gk_player_ids]

# saves90_prior 계산
total_saves = sum(ps.goalkeeping_saves or 0 for ps in gk_stats)
total_gk_minutes = sum(ps.minutes_played or 0 for ps in gk_stats)
saves90_prior = 90 * total_saves / max(total_gk_minutes, 1)

# goals_prevented90_prior 계산
total_prevented = sum(ps.goalkeeping_goals_prevented or 0 for ps in gk_stats)
goals_prevented90_prior = 90 * total_prevented / max(total_gk_minutes, 1)

# clean_sheets90_prior 계산
total_cs = sum(ps.goalkeeping_clean_sheets or 0 for ps in gk_stats)
clean_sheets90_prior = 90 * total_cs / max(total_gk_minutes, 1)
```

#### 3.3.4 overall_prior 계산

```python
# overall_prior: 전체 선수의 섹션 점수 평균을 0~1로 변환
#
# 계산 순서:
# 1. 모든 선수의 5개 섹션 점수를 먼저 계산 (prior 적용 전 raw 점수)
# 2. 전체 평균을 구함
# 3. 0~100 점수를 0~1로 변환

# 구현 방식: 2-pass 계산
# Pass 1: overall_prior = 0.5 (기본값)으로 모든 섹션 점수 계산
# Pass 2: 계산된 섹션 점수들의 평균으로 overall_prior 재계산 후 overall 점수 갱신

# 또는 단순화된 방식: 고정값 0.5 사용 (중립값)
overall_prior = 0.5
```

**✅ 결정**: `overall_prior`는 고정값 **0.5** 사용 (중립값)

- 이유: 2-pass 계산은 복잡도 증가 대비 효과가 미미함
- `shrink` 함수가 출전시간에 따라 자연스럽게 조절하므로 0.5로 충분

---

## 4. 점수 계산 함수 구현

### 4.1 공용 함수

`c.py` 상단에 정의:

```python
import math


def clamp(x: float, lo: float, hi: float) -> float:
    """값을 [lo, hi] 범위로 제한"""
    return min(max(x, lo), hi)


def sdiv(u: float, v: float, eps: float = 1e-9) -> float:
    """안전한 나눗셈 (0 나눗셈 방지)"""
    return u / max(v, eps)


def per90(count: float, minutes: float) -> float:
    """90분 환산"""
    return 90.0 * count / max(minutes, 1.0)


def shrink(x: float, prior: float, n: float, n0: float) -> float:
    """표본 적을 때 사전값으로 수축"""
    return (n * x + n0 * prior) / (n + n0)


def norm01(x: float, lo: float, hi: float) -> float:
    """[lo, hi] 범위를 [0, 1]로 정규화"""
    return clamp((x - lo) / max(hi - lo, 1e-9), 0.0, 1.0)


def score100(features: list[float], weights: list[float]) -> float:
    """가중합을 0~100점으로 환산"""
    s = sum(w * f for w, f in zip(weights, features))
    return 100.0 * clamp(s, 0.0, 1.0)


def wmean(z: list[float], w: list[float]) -> float:
    """가중 산술평균"""
    return sum(wi * zi for wi, zi in zip(w, z))


def wgeom(z: list[float], w: list[float], eps: float = 1e-6) -> float:
    """가중 기하평균 (균형 강제)"""
    return math.exp(sum(wi * math.log(max(zi, eps)) for wi, zi in zip(w, z)))


def blend(a: float, g: float, lam: float = 0.5) -> float:
    """산술평균 + 기하평균 혼합"""
    return (1.0 - lam) * a + lam * g
```

### 4.2 Prior 강도 상수 (n0)

**✅ 결정**: 5경기 기준 (450분)

```python
# Prior strength constants
M0 = 450.0  # minutes prior strength (약 5경기)

# Shooting
NA0_SHOTS = 15.0  # shots attempts prior strength (5경기 기준 조정)
NR0_XG = 0.75  # xG prior strength (5경기 기준 조정)

# Passing
NP0_PASSES = 200.0  # pass attempts prior strength (5경기 기준 조정)
NC0_CROSSES = 15.0  # cross attempts prior strength (5경기 기준 조정)
NL0_LONG = 12.5  # long ball attempts prior strength (5경기 기준 조정)

# Defending
ND0_DUELS = 40.0  # duels prior strength (5경기 기준 조정)
NA0_AERIAL = 20.0  # aerial duels prior strength (5경기 기준 조정)

# Dribbling
ND0_DRIBBLE = 20.0  # dribble attempts prior strength (5경기 기준 조정)
```

### 4.3 섹션별 점수 계산 함수

#### 4.3.1 슈팅 점수

```python
def calculate_shooting_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    """
    슈팅 점수 계산 (0~100)

    f1: npxG90 (위협도)
    f2: non-penalty goals 90 (실제 득점)
    f3: SOT/Shots (정확도)
    f4: goals/xG (결정력)
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
    f3 = norm01(shrink(sdiv(sot, shots), priors.sot_rate_prior, shots, NA0_SHOTS), 0.20, 0.60)
    f4 = norm01(shrink(sdiv(g_np, xg_np), priors.goals_xg_ratio_prior, xg_np, NR0_XG), 0.60, 1.40)

    return score100([f1, f2, f3, f4], [0.40, 0.30, 0.20, 0.10])
```

#### 4.3.2 패스 점수

```python
def calculate_passing_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    """
    패스 점수 계산 (0~100)

    f1: xA90 (창의성)
    f2: chances90 (찬스 생성)
    f3: assists90 (어시스트)
    f4: pass accuracy (패스 정확도)
    f5: cross + long ball accuracy (특수 패스)
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
    f5 = 0.5 * norm01(shrink(cross_acc, priors.cross_acc_prior, ct, NC0_CROSSES), 0.10, 0.35) +
         0.5 * norm01(shrink(long_acc, priors.long_acc_prior, lt, NL0_LONG), 0.30, 0.70)

    return score100([f1, f2, f3, f4, f5], [0.30, 0.20, 0.15, 0.25, 0.10])
```

#### 4.3.3 수비 점수 (필드 플레이어)

```python
def calculate_defending_score_outfield(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    """
    필드 플레이어 수비 점수 계산 (0~100)

    ft: tackles won
    fi: interceptions
    fb: blocked shots
    fr: recoveries
    fd: duel win rate
    fa: aerial win rate
    ff: fouls (감점)
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
```

#### 4.3.4 수비 점수 (골키퍼)

```python
def calculate_defending_score_goalkeeper(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    """
    골키퍼 수비 점수 계산 (0~100)

    f1: saves per 90
    f2: goals prevented per 90
    f3: clean sheets per 90
    """
    m = float(ps.minutes_played or 0)
    if m < 1:
        return 0.0

    saves = float(ps.goalkeeping_saves or 0)
    prevented = float(ps.goalkeeping_goals_prevented or 0)
    cs = float(ps.goalkeeping_clean_sheets or 0)

    f1 = norm01(shrink(per90(saves, m), priors.saves90_prior, m, M0), 0.0, 5.5)
    f2 = norm01(shrink(per90(prevented, m), priors.goals_prevented90_prior, m, M0), -0.3, 0.6)
    f3 = norm01(shrink(per90(cs, m), priors.clean_sheets90_prior, m, M0), 0.0, 0.50)

    return score100([f1, f2, f3], [0.55, 0.25, 0.20])
```

#### 4.3.5 드리블 점수

```python
def calculate_dribbling_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    """
    드리블 점수 계산 (0~100)

    fs: dribble success rate
    fv: dribble volume (per90)
    fw: fouls won (per90)
    fb: box touches (per90)
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
```

#### 4.3.6 규율 점수

```python
def calculate_discipline_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    """
    규율 점수 계산 (0~100)

    적을수록 점수가 높음 (1 - 페널티)
    """
    m = float(ps.minutes_played or 0)
    if m < 1:
        return 100.0  # 출전 안 했으면 페널티 없음

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
```

### 4.4 Overall 점수 계산

**✅ 결정**: PlayerEntity에서 포지션 정보를 가져와서 사용

```python
from football_data_manager.common.enums.position_enum import PositionEnum

# Position-based weights: [shooting, passing, defending, dribbling, discipline]
# PositionEnum: GOALKEEPER, DEFENDER, MIDFIELDER, FORWARD, UNKNOWN
POSITION_WEIGHTS = {
    PositionEnum.FORWARD: [0.35, 0.20, 0.05, 0.30, 0.10],
    PositionEnum.MIDFIELDER: [0.20, 0.35, 0.15, 0.20, 0.10],
    PositionEnum.DEFENDER: [0.05, 0.20, 0.45, 0.10, 0.20],
    PositionEnum.GOALKEEPER: [0.00, 0.10, 0.80, 0.00, 0.10],
    PositionEnum.UNKNOWN: [0.20, 0.25, 0.25, 0.15, 0.15],
}


def calculate_overall_score(
        s_shot: float,
        s_pass: float,
        s_def: float,
        s_drb: float,
        s_disc: float,
        minutes: float,
        position: PositionEnum,
        prior_overall: float,
        m0: float = M0,
        lam: float = 0.5,
) -> float:
    """
    5개 섹션 점수를 종합하여 Overall 점수 계산 (0~100)

    prior_overall: 고정값 0.5 사용 (중립값)
    """
    weights = POSITION_WEIGHTS.get(position, POSITION_WEIGHTS[PositionEnum.UNKNOWN])

    # 0~1 정규화
    z = [s_shot / 100.0, s_pass / 100.0, s_def / 100.0, s_drb / 100.0, s_disc / 100.0]

    # 가중 산술평균 + 가중 기하평균 혼합
    a = wmean(z, weights)
    g = wgeom(z, weights)
    r = blend(a, g, lam=lam)

    # minutes shrink
    r_shrunk = shrink(r, prior_overall, minutes, m0)
    return 100.0 * clamp(r_shrunk, 0.0, 1.0)
```

**✅ 결정**:

- `prior_overall` = 0.5 (고정값, 중립값)
- 산술/기하평균 혼합 비율 lam=0.5 유지

---

## 5. 메인 업데이트 함수

```python
async def update_player_stat_scores(
        repository_container: CommonRepositoryContainer,
) -> list[PlayerStatEntity]:
    """
    모든 시즌의 PlayerStatEntity에 대해 점수를 계산하고 업데이트합니다.

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

        # Step 2: Build player position cache (GK Prior 계산에 필요)
        player_ids = list(set(ps.player_id for ps in player_stats if ps.player_id))
        players = await player_repository.read_by_ids(player_ids)
        player_position_map = {p.id: p.position for p in players}

        # Step 3: Calculate priors for the season
        priors = calculate_season_priors(player_stats, player_position_map)
        print(f"  Priors calculated")

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
```

---

## 6. c.py 전체 구조

```python
# c.py

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
# 1. 공용 함수
# ============================================================

def clamp(x: float, lo: float, hi: float) -> float:
    ...


def sdiv(u: float, v: float, eps: float = 1e-9) -> float:
    ...


def per90(count: float, minutes: float) -> float:
    ...


def shrink(x: float, prior: float, n: float, n0: float) -> float:
    ...


def norm01(x: float, lo: float, hi: float) -> float:
    ...


def score100(features: list[float], weights: list[float]) -> float:
    ...


def wmean(z: list[float], w: list[float]) -> float:
    ...


def wgeom(z: list[float], w: list[float], eps: float = 1e-6) -> float:
    ...


def blend(a: float, g: float, lam: float = 0.5) -> float:
    ...


# ============================================================
# 2. Prior 계산
# ============================================================

@dataclass
class SeasonPriors:
    ...


def calculate_season_priors(
    player_stats: list[PlayerStatEntity],
    player_position_map: dict[int, PositionEnum],
) -> SeasonPriors:
    ...


# ============================================================
# 3. 섹션별 점수 계산
# ============================================================

def calculate_shooting_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    ...


def calculate_passing_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    ...


def calculate_defending_score_outfield(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    ...


def calculate_defending_score_goalkeeper(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    ...


def calculate_dribbling_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    ...


def calculate_discipline_score(ps: PlayerStatEntity, priors: SeasonPriors) -> float:
    ...


# ============================================================
# 4. Overall 점수 계산
# ============================================================

def calculate_overall_score(...) -> float:
    ...


# ============================================================
# 5. 메인 업데이트 함수
# ============================================================

async def update_player_stat_scores(
        repository_container: CommonRepositoryContainer,
) -> list[PlayerStatEntity]:
    ...


# ============================================================
# 6. 실행 진입점
# ============================================================

async def main():
    service_container = CommonServiceContainer()
    service_container.container_config.from_dict({"config_path": "./configs/.env"})
    db_service = service_container.db_service()

    async with db_service.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    repository_container = CommonRepositoryContainer(db_service=db_service)

    await update_player_stat_scores(repository_container)


if __name__ == "__main__":
    run(main())
```

---

## 7. 필요한 Repository 변경 사항

### 7.1 PlayerStatRepository 추가 메서드

| 메서드                      | 설명                   |
|--------------------------|----------------------|
| `read_by_season(season)` | 시즌별 모든 PlayerStat 조회 |

### 7.2 PlayerRepository 추가 메서드

| 메서드                | 설명                            |
|--------------------|-------------------------------|
| `read_by_ids(ids)` | 여러 ID로 Player 일괄 조회 (포지션 캐싱용) |

### 7.3 upsert_player_stat 수정

기존 `upsert_player_stat` 메서드에 score 필드 업데이트 추가:

```python
# 기존 코드에 추가
existing_stat.score_shooting = player_stat_entity.score_shooting
existing_stat.score_passing = player_stat_entity.score_passing
existing_stat.score_defending = player_stat_entity.score_defending
existing_stat.score_dribbling = player_stat_entity.score_dribbling
existing_stat.score_discipline = player_stat_entity.score_discipline
existing_stat.score_overall = player_stat_entity.score_overall
```

---

## 8. 정규화 범위 조정 계획

**✅ 결정**: 2024년 데이터 분포 확인 후 정규화 범위 조정

구현 시 다음 절차를 따릅니다:

1. 2024년 시즌 데이터 로드
2. 각 지표별 분포 분석 (percentile 확인)
3. lo/hi 값 조정 (예: 5th~95th percentile 범위)
4. 조정된 값으로 코드 업데이트

---

## 9. 체크리스트

- [x] `PlayerStatRepository.read_by_season` 메서드 구현
- [x] `PlayerRepository.read_by_ids` 메서드 구현
- [x] `PlayerStatRepository.upsert_player_stat`에 score 필드 업데이트 추가
- [x] `c.py` 공용 함수 구현
- [x] `SeasonPriors` 데이터 클래스 구현
- [x] `calculate_season_priors` 함수 구현 (지표 유형별 계산)
- [x] 5개 섹션 점수 계산 함수 구현
- [x] `calculate_overall_score` 함수 구현 (PositionEnum 사용)
- [ ] 2024년 데이터 분포 분석 및 정규화 범위 조정
- [x] 테스트 실행 및 검증

---

## 10. 결정사항 요약

| 항목            | 결정                                      |
|---------------|-----------------------------------------|
| Prior 계산 방식   | 지표 유형별 분리 (per90: 출전시간 가중, 비율: 분모 합 기준) |
| Prior 강도 (M0) | 450분 (5경기)                              |
| 포지션 정보        | PlayerEntity에서 조회                       |
| 정규화 범위        | 2024년 데이터 분포 확인 후 조정                    |
| Overall 혼합 비율 | lam=0.5 유지                              |
| overall_prior | 0.5 고정값 (중립값)                           |

---

## 11. 참조

- `claudedocs/player-stat-score-chat.md`: 점수 계산 공식 및 상세 설명
- `b.py`: 기존 update 함수 구현 패턴 참조
- `PlayerStatEntity`: 점수 저장 필드 및 통계 필드 정의
- `PlayerEntity`: 포지션 정보 (PositionEnum)
