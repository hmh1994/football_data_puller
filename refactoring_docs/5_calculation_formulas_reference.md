# Calculation Formulas Reference

> **⚠️ CRITICAL**: 이 문서는 리팩토링 중 절대 유실되면 안 됩니다.
> 
> 모든 계산식과 상수는 검증된 값이며, 변경 시 반드시 이 문서를 업데이트해야 합니다.

**Last Updated**: 2026-01-26  
**Source Files**: `c.py`, `b.py`

---

## 목차

1. [Player Stat Scores (6개 점수)](#1-player-stat-scores)
   - 1.1 [Shooting Score](#11-shooting-score)
   - 1.2 [Passing Score](#12-passing-score)
   - 1.3 [Defending Score (Outfield)](#13-defending-score-outfield)
   - 1.4 [Defending Score (Goalkeeper)](#14-defending-score-goalkeeper)
   - 1.5 [Dribbling Score](#15-dribbling-score)
   - 1.6 [Discipline Score](#16-discipline-score)
   - 1.7 [Overall Score](#17-overall-score)
2. [Team Momentum Index](#2-team-momentum-index)
3. [Season Analytics (7개 메트릭)](#3-season-analytics)
4. [Utility Functions](#4-utility-functions)

---

## 1. Player Stat Scores

### 개요

각 `PlayerStatEntity`는 6개의 점수 필드를 가집니다:

| 필드 | 범위 | 설명 |
|------|------|------|
| `score_shooting` | 0~100 | 슛팅 능력 점수 |
| `score_passing` | 0~100 | 패스 능력 점수 |
| `score_defending` | 0~100 | 수비 능력 점수 (포지션별 다름) |
| `score_dribbling` | 0~100 | 드리블 능력 점수 |
| `score_discipline` | 0~100 | 규율 점수 (카드 적을수록 높음) |
| `score_overall` | 0~100 | 종합 점수 (위 5개 점수의 가중 평균) |

**구현 위치**: `c.py`의 `update_player_stat_scores()` 함수

---

### Prior Values (시즌별 기준값)

모든 점수 계산은 **Bayesian Shrinkage**를 사용하여 시즌 평균(Prior)으로 보정됩니다.

#### Prior 계산 방법론

**Source**: `c.py`의 `calculate_season_priors()` 함수

```python
class SeasonPriors:
    """시즌별 Prior 값 (Bayesian Shrinkage용 기준값)"""
    
    # Per90 타입 (90분당 평균)
    prior_goal_per90: float
    prior_assist_per90: float
    prior_key_pass_per90: float
    prior_successful_dribble_per90: float
    prior_successful_cross_per90: float
    prior_tackle_won_per90: float
    prior_interception_per90: float
    prior_blocked_cross_per90: float
    prior_recovery_per90: float
    prior_duel_won_per90: float
    prior_aerial_won_per90: float
    prior_foul_committed_per90: float
    
    # Ratio 타입 (성공률 %)
    prior_shot_accuracy: float
    prior_pass_accuracy: float
    prior_long_pass_accuracy: float
    prior_tackle_success: float
    
    # GK 전용 (골키퍼 Per90)
    prior_gk_save_per90: float
    prior_gk_claim_per90: float
    prior_gk_punch_per90: float
```

#### Prior 계산 공식

**Per90 Prior** (90분당 평균):
```
total_minutes = sum(player_stat.minutes_played for all players)
total_events = sum(player_stat.event_count for all players)

prior_event_per90 = (total_events / total_minutes) × 90
```

**Ratio Prior** (성공률 %):
```
total_attempts = sum(player_stat.attempts for all players)
total_successes = sum(player_stat.successes for all players)

prior_ratio = (total_successes / total_attempts) × 100
```

**GK Prior** (골키퍼만 해당):
```
gk_players = [player for player in players if position == "GK"]
total_gk_minutes = sum(gk.minutes_played for gk in gk_players)
total_gk_events = sum(gk.event_count for gk in gk_players)

prior_gk_event_per90 = (total_gk_events / total_gk_minutes) × 90
```

---

### Bayesian Shrinkage 함수

**Source**: `c.py`

#### `shrink_per90()`

90분당 통계를 Prior로 보정:

```python
def shrink_per90(
    count: int,
    minutes: int,
    prior: float,
    k: float = K_PER90  # 기본값: 270.0
) -> float:
    """
    Bayesian Shrinkage for per-90 stats.
    
    Formula:
    1. k_minutes = k × (prior / 90)
    2. shrunk_value = (count + k_minutes × (prior / 90)) / (minutes + k_minutes) × 90
    
    :param count: 실제 이벤트 발생 횟수
    :param minutes: 선수가 뛴 총 분 수
    :param prior: 시즌 평균 per90 값
    :param k: Shrinkage 강도 상수 (기본값: 270분)
    :returns: Bayesian shrinkage 적용된 per90 값
    """
```

**상수**:
- `K_PER90 = 270.0` (3경기 = 270분)

**예제**:
```python
# 선수가 450분 동안 5골 기록, 시즌 평균 0.5골/90분
shrunk_goal_per90 = shrink_per90(
    count=5,
    minutes=450,
    prior=0.5,
    k=270.0
)

# 계산:
# k_minutes = 270 × (0.5 / 90) = 1.5
# shrunk = (5 + 1.5 × (0.5 / 90)) / (450 + 1.5) × 90
# shrunk = (5 + 0.00833...) / 451.5 × 90
# shrunk ≈ 0.998 goals/90min
```

#### `shrink_ratio()`

성공률 통계를 Prior로 보정:

```python
def shrink_ratio(
    successes: int,
    attempts: int,
    prior: float,
    k: float = K_RATIO  # 기본값: 20.0
) -> float:
    """
    Bayesian Shrinkage for ratio stats (success rate).
    
    Formula:
    shrunk_ratio = (successes + k × prior) / (attempts + k)
    
    :param successes: 성공 횟수
    :param attempts: 시도 횟수
    :param prior: 시즌 평균 성공률 (0~100)
    :param k: Shrinkage 강도 상수 (기본값: 20회)
    :returns: Bayesian shrinkage 적용된 성공률 (0~100)
    """
```

**상수**:
- `K_RATIO = 20.0` (20회 시도)

**예제**:
```python
# 선수가 50번 슛, 25번 성공, 시즌 평균 슛 정확도 40%
shrunk_accuracy = shrink_ratio(
    successes=25,
    attempts=50,
    prior=40.0,
    k=20.0
)

# 계산:
# shrunk = (25 + 20 × 40) / (50 + 20)
# shrunk = (25 + 800) / 70
# shrunk = 825 / 70 ≈ 11.79%  # 잘못된 계산

# 올바른 계산 (prior는 소수):
# prior = 40.0 (%)이면 prior/100 = 0.4
# shrunk = (25 + 20 × 0.4) / (50 + 20) × 100
# shrunk = (25 + 8) / 70 × 100
# shrunk = 33 / 70 × 100 ≈ 47.14%
```

**⚠️ 주의**: `prior` 파라미터는 0~100 범위의 퍼센트 값이지만, 내부 계산에서 0~1 범위로 변환됩니다.

#### `featurize()`

통계를 0~1 범위로 정규화:

```python
def featurize(
    value: float,
    vmin: float,
    vmax: float,
    reverse: bool = False
) -> float:
    """
    Normalize value to 0~1 range.
    
    Formula:
    1. clamped_value = clamp(value, vmin, vmax)
    2. normalized = (clamped_value - vmin) / (vmax - vmin)
    3. if reverse: normalized = 1 - normalized
    
    :param value: 정규화할 값
    :param vmin: 최소값 (0에 매핑)
    :param vmax: 최대값 (1에 매핑)
    :param reverse: True면 높을수록 나쁜 값 (예: 파울)
    :returns: 0~1 범위의 정규화된 값
    """
```

**예제**:
```python
# 골 per90: 0.0~2.0 범위, 실제값 1.0
f = featurize(1.0, vmin=0.0, vmax=2.0, reverse=False)
# f = (1.0 - 0.0) / (2.0 - 0.0) = 0.5

# 파울 per90: 0.0~3.0 범위, 실제값 1.5 (높을수록 나쁨)
f = featurize(1.5, vmin=0.0, vmax=3.0, reverse=True)
# f = 1 - ((1.5 - 0.0) / (3.0 - 0.0)) = 1 - 0.5 = 0.5
```

#### `score100()`

Feature들의 가중 평균을 0~100 점수로 변환:

```python
def score100(features: list[float], weights: list[float]) -> float:
    """
    Calculate weighted sum and convert to 0~100 score.
    
    Formula:
    score = 100 × clamp(sum(f[i] × w[i] for i in range(len(features))), 0, 1)
    
    :param features: Feature 값들 (각각 0~1 범위)
    :param weights: 가중치 (합이 1.0이어야 함)
    :returns: 0~100 범위의 최종 점수
    """
    weighted_sum = sum(f * w for f, w in zip(features, weights))
    return 100.0 * max(0.0, min(1.0, weighted_sum))
```

**예제**:
```python
features = [0.8, 0.6, 0.4]
weights = [0.5, 0.3, 0.2]

score = score100(features, weights)
# weighted_sum = 0.8×0.5 + 0.6×0.3 + 0.4×0.2 = 0.4 + 0.18 + 0.08 = 0.66
# score = 100 × 0.66 = 66.0
```

---

### 1.1 Shooting Score

**Source**: `c.py`의 `calculate_shooting_score()` 함수

#### 공식

```
1. goal_shrunk = shrink_per90(goals, minutes, prior_goal_per90, k=270)
2. shot_acc_shrunk = shrink_ratio(ontarget_shots, total_shots, prior_shot_acc, k=20)
3. xg_per90 = (expected_goals / minutes) × 90  # No shrinkage
4. npxg_per90 = (expected_goals_non_penalty / minutes) × 90  # No shrinkage

5. f1 = featurize(goal_shrunk, vmin=0.0, vmax=2.0)
6. f2 = featurize(shot_acc_shrunk, vmin=20.0, vmax=80.0)
7. f3 = featurize(xg_per90, vmin=0.0, vmax=2.0)
8. f4 = featurize(npxg_per90, vmin=0.0, vmax=1.5)

9. score = 100 × (0.40×f1 + 0.30×f2 + 0.20×f3 + 0.10×f4)
```

#### 가중치

| Feature | Weight | 설명 |
|---------|--------|------|
| Goals per90 (shrunk) | 0.40 | 실제 골 (Bayesian 보정) |
| Shot accuracy (shrunk) | 0.30 | 슛 정확도 (Bayesian 보정) |
| xG per90 | 0.20 | Expected Goals (보정 없음) |
| npxG per90 | 0.10 | Non-penalty xG (보정 없음) |

#### 정규화 범위

| Metric | vmin | vmax |
|--------|------|------|
| Goals per90 | 0.0 | 2.0 |
| Shot accuracy (%) | 20.0 | 80.0 |
| xG per90 | 0.0 | 2.0 |
| npxG per90 | 0.0 | 1.5 |

#### 예제

```python
# Player A: 900분 동안 10골, 슛 30/50 (60% 정확도)
# xG: 8.0, npxG: 6.5
# Prior: goal_per90=0.5, shot_acc=40%

# Step 1-4: Shrinkage
goal_shrunk = shrink_per90(10, 900, 0.5, 270)
# = (10 + 270×(0.5/90)) / (900 + 270) × 90
# = (10 + 1.5) / 1170 × 90 ≈ 0.885

shot_acc_shrunk = shrink_ratio(30, 50, 40.0, 20)
# = (30 + 20×0.4) / (50 + 20) × 100
# = 38 / 70 × 100 ≈ 54.29%

xg_per90 = (8.0 / 900) × 90 = 0.8
npxg_per90 = (6.5 / 900) × 90 ≈ 0.65

# Step 5-8: Featurize
f1 = featurize(0.885, 0.0, 2.0) = 0.885 / 2.0 ≈ 0.443
f2 = featurize(54.29, 20.0, 80.0) = (54.29 - 20) / 60 ≈ 0.571
f3 = featurize(0.8, 0.0, 2.0) = 0.8 / 2.0 = 0.4
f4 = featurize(0.65, 0.0, 1.5) = 0.65 / 1.5 ≈ 0.433

# Step 9: Score
score = 100 × (0.40×0.443 + 0.30×0.571 + 0.20×0.4 + 0.10×0.433)
     = 100 × (0.177 + 0.171 + 0.08 + 0.043)
     = 100 × 0.471
     ≈ 47.1
```

---

### 1.2 Passing Score

**Source**: `c.py`의 `calculate_passing_score()` 함수

#### 공식

```
1. assist_shrunk = shrink_per90(assists, minutes, prior_assist_per90, k=270)
2. key_pass_shrunk = shrink_per90(key_passes, minutes, prior_key_pass_per90, k=270)
3. pass_acc_shrunk = shrink_ratio(accurate_passes, total_passes, prior_pass_acc, k=20)
4. long_pass_acc_shrunk = shrink_ratio(accurate_long_passes, total_long_passes, prior_long_pass_acc, k=20)
5. cross_shrunk = shrink_per90(successful_crosses, minutes, prior_successful_cross_per90, k=270)

6. f1 = featurize(assist_shrunk, vmin=0.0, vmax=1.0)
7. f2 = featurize(key_pass_shrunk, vmin=0.0, vmax=4.0)
8. f3 = featurize(pass_acc_shrunk, vmin=50.0, vmax=95.0)
9. f4 = featurize(long_pass_acc_shrunk, vmin=30.0, vmax=85.0)
10. f5 = featurize(cross_shrunk, vmin=0.0, vmax=3.0)

11. score = 100 × (0.30×f1 + 0.20×f2 + 0.15×f3 + 0.25×f4 + 0.10×f5)
```

#### 가중치

| Feature | Weight | 설명 |
|---------|--------|------|
| Assists per90 (shrunk) | 0.30 | 어시스트 |
| Key passes per90 (shrunk) | 0.20 | 키패스 |
| Pass accuracy (shrunk) | 0.15 | 패스 정확도 |
| Long pass accuracy (shrunk) | 0.25 | 롱패스 정확도 |
| Successful crosses per90 (shrunk) | 0.10 | 성공한 크로스 |

#### 정규화 범위

| Metric | vmin | vmax |
|--------|------|------|
| Assists per90 | 0.0 | 1.0 |
| Key passes per90 | 0.0 | 4.0 |
| Pass accuracy (%) | 50.0 | 95.0 |
| Long pass accuracy (%) | 30.0 | 85.0 |
| Successful crosses per90 | 0.0 | 3.0 |

---

### 1.3 Defending Score (Outfield)

**Source**: `c.py`의 `calculate_defending_score_outfield()` 함수

**⚠️ 중요**: 골키퍼가 아닌 필드 플레이어용 공식입니다.

#### 공식

```
1. tackle_shrunk = shrink_per90(tackles_won, minutes, prior_tackle_won_per90, k=270)
2. interception_shrunk = shrink_per90(interceptions, minutes, prior_interception_per90, k=270)
3. blocked_cross_shrunk = shrink_per90(blocked_crosses, minutes, prior_blocked_cross_per90, k=270)
4. tackle_success_shrunk = shrink_ratio(tackles_won, total_tackles, prior_tackle_success, k=20)
5. recovery_shrunk = shrink_per90(recoveries, minutes, prior_recovery_per90, k=270)
6. duel_won_shrunk = shrink_per90(duels_won, minutes, prior_duel_won_per90, k=270)
7. aerial_won_shrunk = shrink_per90(aerials_won, minutes, prior_aerial_won_per90, k=270)
8. foul_shrunk = shrink_per90(fouls_committed, minutes, prior_foul_committed_per90, k=270)

9. ft = featurize(tackle_shrunk, vmin=0.0, vmax=6.0)
10. fi = featurize(interception_shrunk, vmin=0.0, vmax=4.0)
11. fb = featurize(blocked_cross_shrunk, vmin=0.0, vmax=2.0)
12. fr = featurize(tackle_success_shrunk, vmin=30.0, vmax=90.0)
13. fd = featurize(recovery_shrunk, vmin=0.0, vmax=15.0)
14. fa = featurize(aerial_won_shrunk, vmin=0.0, vmax=8.0)
15. ff = featurize(foul_shrunk, vmin=0.0, vmax=3.0, reverse=True)  # 파울은 적을수록 좋음

16. score = 100 × clamp(0.22×ft + 0.18×fi + 0.12×fb + 0.18×fr + 0.20×fd + 0.10×fa - 0.10×ff, 0, 1)
```

**⚠️ 주의**: 파울 feature는 **음의 가중치**(`-0.10`)를 가집니다.

#### 가중치

| Feature | Weight | 설명 |
|---------|--------|------|
| Tackles won per90 (shrunk) | +0.22 | 태클 성공 |
| Interceptions per90 (shrunk) | +0.18 | 인터셉트 |
| Blocked crosses per90 (shrunk) | +0.12 | 크로스 차단 |
| Tackle success rate (shrunk) | +0.18 | 태클 성공률 |
| Recoveries per90 (shrunk) | +0.20 | 볼 회수 |
| Aerials won per90 (shrunk) | +0.10 | 공중볼 성공 |
| Fouls committed per90 (shrunk) | **-0.10** | 파울 (페널티) |

**합계**: 0.22 + 0.18 + 0.12 + 0.18 + 0.20 + 0.10 - 0.10 = **0.90**

#### 정규화 범위

| Metric | vmin | vmax | reverse |
|--------|------|------|---------|
| Tackles won per90 | 0.0 | 6.0 | No |
| Interceptions per90 | 0.0 | 4.0 | No |
| Blocked crosses per90 | 0.0 | 2.0 | No |
| Tackle success (%) | 30.0 | 90.0 | No |
| Recoveries per90 | 0.0 | 15.0 | No |
| Aerials won per90 | 0.0 | 8.0 | No |
| Fouls committed per90 | 0.0 | 3.0 | **Yes** |

---

### 1.4 Defending Score (Goalkeeper)

**Source**: `c.py`의 `calculate_defending_score_goalkeeper()` 함수

**⚠️ 중요**: 골키퍼 전용 공식입니다.

#### 공식

```
1. save_shrunk = shrink_per90(saves, minutes, prior_gk_save_per90, k=270)
2. claim_shrunk = shrink_per90(claims, minutes, prior_gk_claim_per90, k=270)
3. punch_shrunk = shrink_per90(punches, minutes, prior_gk_punch_per90, k=270)

4. f1 = featurize(save_shrunk, vmin=0.0, vmax=10.0)
5. f2 = featurize(claim_shrunk, vmin=0.0, vmax=3.0)
6. f3 = featurize(punch_shrunk, vmin=0.0, vmax=2.0)

7. score = 100 × (0.55×f1 + 0.25×f2 + 0.20×f3)
```

#### 가중치

| Feature | Weight | 설명 |
|---------|--------|------|
| Saves per90 (shrunk) | 0.55 | 선방 |
| Claims per90 (shrunk) | 0.25 | 크로스 캐치 |
| Punches per90 (shrunk) | 0.20 | 펀칭 |

#### 정규화 범위

| Metric | vmin | vmax |
|--------|------|------|
| Saves per90 | 0.0 | 10.0 |
| Claims per90 | 0.0 | 3.0 |
| Punches per90 | 0.0 | 2.0 |

---

### 1.5 Dribbling Score

**Source**: `c.py`의 `calculate_dribbling_score()` 함수

#### 공식

```
1. successful_dribble_shrunk = shrink_per90(successful_dribbles, minutes, prior_successful_dribble_per90, k=270)
2. won_contest_shrunk = shrink_per90(won_contests, minutes, prior_duel_won_per90, k=270)
3. dispossessed_shrunk = shrink_per90(dispossessed_count, minutes, 1.5, k=270)  # Prior 하드코딩
4. ball_touch_shrunk = shrink_per90(ball_touches, minutes, 60.0, k=270)  # Prior 하드코딩

5. fs = featurize(successful_dribble_shrunk, vmin=0.0, vmax=5.0)
6. fv = featurize(won_contest_shrunk, vmin=0.0, vmax=10.0)
7. fw = featurize(dispossessed_shrunk, vmin=0.0, vmax=3.0, reverse=True)  # 빼앗김은 적을수록 좋음
8. fb = featurize(ball_touch_shrunk, vmin=10.0, vmax=100.0)

9. score = 100 × (0.35×fs + 0.30×fv + 0.20×fw + 0.15×fb)
```

**⚠️ 주의**: `dispossessed`와 `ball_touch`의 Prior는 하드코딩되어 있습니다 (1.5, 60.0).

#### 가중치

| Feature | Weight | 설명 |
|---------|--------|------|
| Successful dribbles per90 (shrunk) | 0.35 | 성공한 드리블 |
| Won contests per90 (shrunk) | 0.30 | 몸싸움 승리 |
| Dispossessed per90 (shrunk) | 0.20 | 볼 빼앗김 (적을수록 좋음) |
| Ball touches per90 (shrunk) | 0.15 | 볼 터치 |

#### 정규화 범위

| Metric | vmin | vmax | reverse |
|--------|------|------|---------|
| Successful dribbles per90 | 0.0 | 5.0 | No |
| Won contests per90 | 0.0 | 10.0 | No |
| Dispossessed per90 | 0.0 | 3.0 | **Yes** |
| Ball touches per90 | 10.0 | 100.0 | No |

---

### 1.6 Discipline Score

**Source**: `c.py`의 `calculate_discipline_score()` 함수

#### 공식

```
1. yellow_shrunk = shrink_per90(yellow_cards, minutes, prior_yellow_per90, k=270)
2. red_shrunk = shrink_per90(red_cards, minutes, prior_red_per90, k=270)

3. penalty = (yellow_shrunk / 3.0) + (red_shrunk / 0.3)
4. penalty_clamped = clamp(penalty, 0.0, 1.0)

5. score = 100 × (1 - penalty_clamped)
```

**상수**:
- Yellow card penalty coefficient: `3.0` (90분당 3장 = 100% 페널티)
- Red card penalty coefficient: `0.3` (90분당 0.3장 = 100% 페널티)

#### 예제

```python
# Player: 900분 동안 옐로우 3장, 레드 0장
# Prior: yellow_per90=1.0, red_per90=0.05

yellow_shrunk = shrink_per90(3, 900, 1.0, 270)
# ≈ (3 + 270×(1.0/90)) / (900 + 270) × 90
# ≈ (3 + 3.0) / 1170 × 90 ≈ 0.462

red_shrunk = shrink_per90(0, 900, 0.05, 270)
# ≈ (0 + 270×(0.05/90)) / (900 + 270) × 90
# ≈ (0 + 0.15) / 1170 × 90 ≈ 0.0115

penalty = (0.462 / 3.0) + (0.0115 / 0.3)
        = 0.154 + 0.038
        = 0.192

score = 100 × (1 - 0.192) = 80.8
```

---

### 1.7 Overall Score

**Source**: `c.py`의 `calculate_overall_score()` 함수

종합 점수는 5개 섹션 점수(shooting, passing, defending, dribbling, discipline)의 **포지션별 가중 평균**입니다.

#### 공식

```
1. 섹션 점수 정규화: z[i] = section_score[i] / 100  (0~1 범위로 변환)

2. 포지션별 가중치 적용:
   w_shot, w_pass, w_def, w_drb, w_disc = get_weights_by_position(position)

3. 가중 평균 계산:
   r = w_shot×z_shot + w_pass×z_pass + w_def×z_def + w_drb×z_drb + w_disc×z_disc

4. Bayesian Shrinkage (Overall용):
   r_shrunk = (r × minutes + K_OVERALL × 0.5) / (minutes + K_OVERALL)
   
   여기서 K_OVERALL = 450 (5경기), Prior = 0.5 (중간값)

5. Clamp 및 점수 변환:
   r_clamped = clamp(r_shrunk, 0.0, 1.0)
   
6. 최종 점수:
   score = 100 × r_clamped
```

#### 상수

- `K_OVERALL = 450.0` (5경기 = 450분)
- `OVERALL_PRIOR = 0.5` (0~1 범위에서 중간값)

#### 포지션별 가중치

**Source**: `c.py`의 `POSITION_WEIGHTS` 딕셔너리

| Position | Shooting | Passing | Defending | Dribbling | Discipline | 합계 |
|----------|----------|---------|-----------|-----------|------------|------|
| **Goalkeeper (GK)** | 0.0 | 0.1 | 0.6 | 0.0 | 0.3 | 1.0 |
| **Defender (D)** | 0.1 | 0.2 | 0.5 | 0.1 | 0.1 | 1.0 |
| **Midfielder (M)** | 0.2 | 0.3 | 0.2 | 0.2 | 0.1 | 1.0 |
| **Forward (F)** | 0.4 | 0.2 | 0.1 | 0.2 | 0.1 | 1.0 |

**매핑 규칙** (PositionEnum → 가중치):
```python
POSITION_WEIGHTS = {
    PositionEnum.GOALKEEPER: (0.0, 0.1, 0.6, 0.0, 0.3),
    PositionEnum.DEFENDER: (0.1, 0.2, 0.5, 0.1, 0.1),
    PositionEnum.MIDFIELDER: (0.2, 0.3, 0.2, 0.2, 0.1),
    PositionEnum.FORWARD: (0.4, 0.2, 0.1, 0.2, 0.1),
}
# 순서: (shooting, passing, defending, dribbling, discipline)
```

#### 예제

```python
# Midfielder: 900분 플레이
# Section scores: shooting=60, passing=75, defending=50, dribbling=70, discipline=80

# Step 1: Normalize
z_shot = 60 / 100 = 0.6
z_pass = 75 / 100 = 0.75
z_def = 50 / 100 = 0.5
z_drb = 70 / 100 = 0.7
z_disc = 80 / 100 = 0.8

# Step 2: Weights (Midfielder)
w_shot = 0.2, w_pass = 0.3, w_def = 0.2, w_drb = 0.2, w_disc = 0.1

# Step 3: Weighted average
r = 0.2×0.6 + 0.3×0.75 + 0.2×0.5 + 0.2×0.7 + 0.1×0.8
  = 0.12 + 0.225 + 0.1 + 0.14 + 0.08
  = 0.665

# Step 4: Bayesian Shrinkage
r_shrunk = (0.665 × 900 + 450 × 0.5) / (900 + 450)
         = (598.5 + 225) / 1350
         = 823.5 / 1350
         ≈ 0.610

# Step 5: Clamp (이미 0~1 범위 내)
r_clamped = 0.610

# Step 6: Final score
overall_score = 100 × 0.610 = 61.0
```

---

## 2. Team Momentum Index

**Source**: `b.py`의 `update_momentum()` 함수

### 개요

팀의 최근 경기 폼을 나타내는 지표입니다.

**저장 위치**: `TeamStatEntity.momentum` (Double, nullable)

**범위**: 대략 -100 ~ +100 (이론적으로는 unbounded, but `tanh`로 인해 수렴)

### 공식

```
1. ΔPPM = PPM(recent N matches) - PPM(season average)
   where PPM = Points Per Match

2. ΔxG = average xG difference over N matches
   where xG difference = team_xG - opponent_xG

3. z(ΔPPM) = z-score normalization across all teams in season
4. z(ΔxG) = z-score normalization across all teams in season

5. Combined z-score:
   z_combined = 0.6 × z(ΔPPM) + 0.4 × z(ΔxG)

6. Momentum:
   Momentum = 100 × tanh(β × z_combined)
```

### 파라미터

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `window_size` (N) | 5 | 최근 N경기 사용 |
| `beta` (β) | 0.5 | Scaling factor (조정 강도) |

### 상세 계산 단계

#### Step 1: ΔPPM 계산

```python
# Season PPM
ppm_season = overall_points / overall_matches

# Recent PPM from cumulative points
cumulative = overall_cumulative_points  # List[int]
M = len(cumulative)  # Total matches played
N = min(window_size, M)  # Effective window

if M > N:
    points_recent = cumulative[-1] - cumulative[-(N+1)]
else:
    points_recent = cumulative[-1]  # All matches are within window

ppm_recent = points_recent / N

# Delta
delta_ppm = ppm_recent - ppm_season
```

**예제**:
```python
# Team played 10 matches, cumulative points: [3, 4, 7, 8, 11, 12, 15, 16, 19, 22]
# window_size = 5

cumulative = [3, 4, 7, 8, 11, 12, 15, 16, 19, 22]
M = 10
N = 5

# Season PPM
ppm_season = 22 / 10 = 2.2

# Recent PPM (last 5 matches)
points_recent = cumulative[-1] - cumulative[-(5+1)]
              = 22 - 11
              = 11

ppm_recent = 11 / 5 = 2.2

# Delta
delta_ppm = 2.2 - 2.2 = 0.0
```

#### Step 2: ΔxG 계산

```python
# Get recent N matches
match_associations = sorted(team_stat.match_associations, key=lambda x: x.kickoff_time)
recent_associations = match_associations[-N:]

xg_diffs = []
for assoc in recent_associations:
    match = await match_repository.read_by_id(assoc.match_id)
    match_stats = await match_stat_repository.read_by_match(match)
    
    # Find team's xG and opponent's xG
    for stat in match_stats:
        if stat.team_id == team_stat.team_id:
            team_xg = stat.expected_goals
        else:
            opponent_xg = stat.expected_goals
    
    if team_xg is not None and opponent_xg is not None:
        xg_diffs.append(team_xg - opponent_xg)

delta_xg = sum(xg_diffs) / len(xg_diffs) if xg_diffs else None
```

#### Step 3: Z-score Normalization

모든 팀의 ΔPPM, ΔxG를 모아서 z-score 정규화:

```python
def calculate_z_scores(values: list[float | None], valid_values: list[float]) -> list[float | None]:
    if len(valid_values) < 2:
        return [None] * len(values)  # Not enough data
    
    mean = sum(valid_values) / len(valid_values)
    variance = sum((v - mean) ** 2 for v in valid_values) / len(valid_values)
    std = sqrt(variance) if variance > 0 else 1.0
    
    return [(v - mean) / std if v is not None else None for v in values]

z_ppm = calculate_z_scores(ppm_deltas, valid_ppm)
z_xg = calculate_z_scores(xg_deltas, valid_xg)
```

#### Step 4: Final Momentum

```python
if z_ppm[i] is not None and z_xg[i] is not None:
    combined_z = 0.6 * z_ppm[i] + 0.4 * z_xg[i]
    momentum = 100 * math.tanh(beta * combined_z)
else:
    momentum = None
```

### 가중치

| Component | Weight |
|-----------|--------|
| z(ΔPPM) | 0.6 |
| z(ΔxG) | 0.4 |

### 해석

| Momentum | 의미 |
|----------|------|
| +50 ~ +100 | 매우 좋은 폼 (최근 성적이 시즌 평균보다 훨씬 좋음) |
| +20 ~ +50 | 좋은 폼 |
| -20 ~ +20 | 보통 폼 (시즌 평균과 비슷) |
| -50 ~ -20 | 나쁜 폼 |
| -100 ~ -50 | 매우 나쁜 폼 |

### 예제

```python
# Season: 20 teams
# Team A: ΔPPM = +0.5, ΔxG = +0.3
# League average ΔPPM: 0.0, std: 0.4
# League average ΔxG: 0.0, std: 0.5

# Z-scores
z_ppm = (0.5 - 0.0) / 0.4 = 1.25
z_xg = (0.3 - 0.0) / 0.5 = 0.6

# Combined
z_combined = 0.6 × 1.25 + 0.4 × 0.6 = 0.75 + 0.24 = 0.99

# Momentum (beta = 0.5)
momentum = 100 × tanh(0.5 × 0.99)
         = 100 × tanh(0.495)
         ≈ 100 × 0.458
         ≈ 45.8
```

---

## 3. Season Analytics

**Source**: `b.py`의 `upsert_analytics()` 함수

### 개요

시즌별 리그 전체 통계를 계산합니다.

**저장 위치**: `AnalyticsEntity` 테이블

**키 타입**: `AnalyticsKeyEnum`

### 7개 메트릭

#### 3.1 PER_MATCH_GOALS

**공식**:
```
total_goals = sum(match.home_team_score + match.away_team_score for all completed matches)
match_count = count(completed matches)

per_match_goals = total_goals / match_count
```

**설명**: 경기당 평균 골 수

**예제**:
```python
# Season: 380 matches, 1050 total goals
per_match_goals = 1050 / 380 ≈ 2.76
```

---

#### 3.2 PER_MATCH_PASS_ACCURACY

**공식**:
```
for each match_stat:
    if passes_total > 0:
        accuracy = (passes_accurate / passes_total) × 100
        total_pass_accuracy += accuracy
        pass_accuracy_count += 1

per_match_pass_accuracy = total_pass_accuracy / pass_accuracy_count
```

**설명**: 경기당 평균 패스 정확도 (%)

**⚠️ 주의**: Match stat 단위로 계산 (팀별), 각 경기는 2개의 match stat을 가짐

**예제**:
```python
# Season: 380 matches × 2 teams = 760 match_stats
# Total pass accuracy sum: 65000%
per_match_pass_accuracy = 65000 / 760 ≈ 85.5%
```

---

#### 3.3 PER_MATCH_SUBSTITUTIONS

**공식**:
```
total_substitutions = 0
for each match:
    total_substitutions += count(match.substitution_associations)

per_match_substitutions = total_substitutions / match_count
```

**설명**: 경기당 평균 교체 수

**예제**:
```python
# Season: 380 matches, 2280 total substitutions
per_match_substitutions = 2280 / 380 = 6.0
```

---

#### 3.4 PER_MATCH_XG

**공식**:
```
total_xg = sum(match_stat.expected_goals for all match_stats)

per_match_xg = total_xg / match_count
```

**설명**: 경기당 평균 기대 득점 (xG)

**⚠️ 주의**: Match stat 단위로 합산 (팀별), 경기당 평균은 match_count로 나눔

**예제**:
```python
# Season: 380 matches, 760 match_stats, total xG: 950
per_match_xg = 950 / 380 ≈ 2.5
```

---

#### 3.5 PER_MATCH_YELLOW_CARDS

**공식**:
```
total_yellow_cards = sum(match_stat.discipline_yellow_cards for all match_stats)

per_match_yellow_cards = total_yellow_cards / match_count
```

**설명**: 경기당 평균 옐로우 카드 수

**예제**:
```python
# Season: 380 matches, 1520 total yellow cards
per_match_yellow_cards = 1520 / 380 = 4.0
```

---

#### 3.6 TOTAL_GOALS

**공식**:
```
total_goals = sum(match.home_team_score + match.away_team_score for all completed matches)
```

**설명**: 시즌 총 골 수

**예제**:
```python
# Season: 1050 total goals
total_goals = 1050
```

---

#### 3.7 TOTAL_RED_CARDS

**공식**:
```
total_red_cards = sum(match_stat.discipline_red_cards for all match_stats)
```

**설명**: 시즌 총 레드 카드 수

**예제**:
```python
# Season: 38 total red cards
total_red_cards = 38
```

---

### Delta 계산

각 Analytics는 이전 시즌과의 변화율(`delta`)을 가집니다:

**공식**:
```python
if previous_season_value exists:
    if previous_season_value == 0:
        delta = None  # Avoid division by zero
    else:
        delta = ((current_value - previous_value) / previous_value) × 100
else:
    delta = None  # First season
```

**예제**:
```python
# Previous season: PER_MATCH_GOALS = 2.5
# Current season: PER_MATCH_GOALS = 2.76

delta = ((2.76 - 2.5) / 2.5) × 100
      = (0.26 / 2.5) × 100
      = 10.4%  # 10.4% 증가
```

---

## 4. Utility Functions

### 4.1 `clamp()`

**Source**: `c.py`

```python
def clamp(value: float, vmin: float, vmax: float) -> float:
    """
    Clamp value to [vmin, vmax] range.
    
    :param value: Value to clamp
    :param vmin: Minimum value
    :param vmax: Maximum value
    :returns: Clamped value
    """
    return max(vmin, min(vmax, value))
```

**예제**:
```python
clamp(1.5, 0.0, 1.0) = 1.0
clamp(-0.5, 0.0, 1.0) = 0.0
clamp(0.7, 0.0, 1.0) = 0.7
```

---

### 4.2 Z-score Normalization

**Source**: `b.py`의 `calculate_z_scores()` (momentum 계산 내부)

```python
def calculate_z_scores(
    values: list[float | None],
    valid_values: list[float]
) -> list[float | None]:
    """
    Calculate z-scores for normalization.
    
    Formula:
    z[i] = (values[i] - mean) / std
    
    :param values: All values (may contain None)
    :param valid_values: Non-None values for mean/std calculation
    :returns: Z-score normalized values
    """
    if len(valid_values) < 2:
        return [None] * len(values)
    
    mean = sum(valid_values) / len(valid_values)
    variance = sum((v - mean) ** 2 for v in valid_values) / len(valid_values)
    std = math.sqrt(variance) if variance > 0 else 1.0
    
    return [(v - mean) / std if v is not None else None for v in values]
```

**예제**:
```python
values = [1.0, 2.0, None, 3.0, 4.0]
valid_values = [1.0, 2.0, 3.0, 4.0]

mean = (1.0 + 2.0 + 3.0 + 4.0) / 4 = 2.5
variance = ((1.0-2.5)² + (2.0-2.5)² + (3.0-2.5)² + (4.0-2.5)²) / 4
         = (2.25 + 0.25 + 0.25 + 2.25) / 4
         = 1.25
std = sqrt(1.25) ≈ 1.118

z_scores = [
    (1.0 - 2.5) / 1.118 ≈ -1.34,
    (2.0 - 2.5) / 1.118 ≈ -0.45,
    None,
    (3.0 - 2.5) / 1.118 ≈ 0.45,
    (4.0 - 2.5) / 1.118 ≈ 1.34
]
```

---

### 4.3 `tanh()`

**Source**: Python `math.tanh()`

**용도**: Team Momentum 계산에서 z-score를 -1~1 범위로 squashing

**특성**:
- `tanh(0) = 0`
- `tanh(±∞) = ±1`
- `tanh(±1) ≈ ±0.76`
- `tanh(±2) ≈ ±0.96`

**그래프**:
```
  1.0 |           ___________
      |         /
      |        /
  0.5 |       /
      |      /
  0.0 |-----/---------------
      |    /
 -0.5 |   /
      |  /
 -1.0 |_/___________
      -4  -2   0   2   4
```

---

## 변경 이력

### 2026-01-26
- 최초 작성: Player Stat Scores, Team Momentum, Season Analytics 전체 문서화
- Source: `c.py`, `b.py`

---

## 참고 사항

### 리팩토링 시 주의사항

1. **상수 변경 금지**: `K_PER90`, `K_RATIO`, `K_OVERALL` 등 모든 상수는 검증된 값입니다.
2. **가중치 변경 금지**: 모든 feature 가중치는 튜닝된 값입니다.
3. **Prior 하드코딩**: Dribbling score의 `dispossessed` (1.5), `ball_touch` (60.0) Prior는 하드코딩되어 있습니다.
4. **포지션 매핑**: `POSITION_WEIGHTS`는 4가지 포지션만 지원합니다 (GK, D, M, F).
5. **Momentum 요구사항**: 최소 2팀 이상의 데이터가 있어야 z-score 계산 가능합니다.

### 테스트 시 검증 항목

- [ ] Player stat scores: 모든 점수가 0~100 범위 내
- [ ] Overall score: 포지션별 가중치 합이 1.0
- [ ] Defending score (Outfield): 파울 페널티 적용 확인
- [ ] Momentum: z-score 정규화 정확성
- [ ] Analytics delta: 이전 시즌 값 참조 정확성
- [ ] Prior 계산: 시즌별 분리 계산
- [ ] Bayesian shrinkage: 적은 샘플에서 Prior로 수렴

---

**EOF**
