# 소스 데이터 문제

**양쪽 데이터가 모두 존재**하지만 서로 불일치하는 케이스. Validator 로직은 정상이며, 소스 API의 데이터 자체가 inconsistent함.

---

## 1. 골 이벤트 vs 스코어 불일치 (125건)

| 체크명                                               | Entity | 건수 |
|---------------------------------------------------|--------|----|
| `home goals from associations == home_team_score` | match  | 62 |
| `away goals from associations == away_team_score` | match  | 63 |

### 현상

goal_association 레코드의 골 합산이 match score와 다름. **양쪽 데이터 모두 존재**하지만 불일치.

### 예시

```
expected=3, actual=2  → 1골 association 누락
expected=0, actual=1  → 없어야 할 association 존재
expected=5, actual=3  → 2골 association 누락
expected=1, actual=2  → 1골 association 초과
```

### 원인

- own goal 처리는 validator에서 정상 반영 (is_own_goal → 상대팀 득점 처리)
- 소스 API에서 goal event 데이터와 match score가 독립적으로 관리되어 동기화 안 됨
- 일부 골 이벤트가 누락되거나 중복 기록됨

### 참고

62개 실패 경기 중 61개가 `goal scorer belongs to lineup or bench` 실패와 겹침.

---

## 2. 골 득점자 라인업 불일치 (66건)

| 체크명                                      | Entity | 건수 |
|------------------------------------------|--------|----|
| `goal scorer belongs to lineup or bench` | match  | 66 |

### 현상

골을 넣은 선수가 해당 경기의 lineup/bench에 없음. **해당 경기는 lineup 데이터가 정상 존재** (lineup size==11, formation PASS).

### 검증

```
# 실패 경기 샘플 — lineup 데이터 정상
[PASS] home lineup size == 11
[PASS] away lineup size == 11
[PASS] home_team_formation sum == 10
[PASS] away_team_formation sum == 10
[FAIL] goal scorer belongs to lineup or bench - player_id=...
```

### 원인

- 소스 API에서 goal event의 player_id와 lineup의 player_id가 불일치
- 선수 교체 관련 이벤트 누락 (교체로 들어온 선수가 bench 목록에 없는 경우)
- 50+ 고유 player_id에서 발생 — 특정 선수 데이터 문제가 아닌 구조적 문제

---

## 3. team_stat vs match_stat 집계 불일치 (158건)

team_stat(시즌 합산)과 match_stat(경기별 합산)이 양쪽 모두 존재하지만 값이 다른 케이스. team_stat은 갱신되었으나 match_stat은 미갱신되었거나, 소스 API에서 집계 기준이 다를 수
있음.

| 체크명                                                                     | Entity    | 건수 | 패턴                   |
|-------------------------------------------------------------------------|-----------|----|----------------------|
| `overall_stat_attack_total_shots == sum(match_stat shots_total)`        | team-stat | 40 | expected > actual 일관 |
| `overall_stat_defense_blocks == sum(match_stat defense_blocks)`         | team-stat | 40 | 양방향 불일치              |
| `overall_stat_defense_tackles == sum(match_stat defense_tackles_total)` | team-stat | 40 | 양방향 불일치              |
| `overall_stat_attack_corners == sum(match_stat corners)`                | team-stat | 21 | actual이 1~3 더 큼      |
| `overall_goals_for ~= sum(PlayerStat.shooting_goals)`                   | team-stat | 15 | tolerance=2 초과       |
| `overall_stat_defense_tackles_successful == ...`                        | team-stat | 1  | 차이 1                 |
| `overall_stat_discipline_yellow_cards == ...`                           | team-stat | 1  | 차이 1                 |

### 패턴별 분석

**`total_shots`** (40건): expected(team_stat) 항상 > actual(sum match_stat)

- team_stat은 소스 API에서 시즌 집계로 가져온 값
- match_stat은 개별 경기별로 가져온 값
- team_stat이 갱신되었으나 일부 경기의 match_stat이 미갱신 → 합산 부족

**`blocks`, `tackles`** (80건): 양방향 불일치 (expected > actual도 있고, expected < actual도 있음)

- 소스 API에서 team_stat과 match_stat의 필드 정의/집계 범위가 다를 가능성
- `defense_blocks`와 `defense_tackles_total`의 포함 범위가 team_stat/match_stat에서 상이

**`corners`** (21건): actual이 expected보다 1~3 더 큼

- 미세한 집계 차이. 소스 API의 보정이 team_stat에만 반영되었을 가능성

**`goals_for vs PlayerStat`** (15건): tolerance=2를 초과하는 차이

- player_stat의 shooting_goals 포함 범위가 team_stat의 goals_for와 다름 (예: penalty 포함 기준)

**`yellow_cards`, `tackles_successful`** (각 1건): 차이 1

- 미세 집계 차이

---

## 4. 수비 듀얼 합산 불일치 (1건)

| 체크명                                              | Entity      | 건수 |
|--------------------------------------------------|-------------|----|
| `defending_duels_won == aerial_won + ground_won` | player-stat | 1  |

### 현상

```
expected=25, actual=24 — 차이 1
```

### 원인

단일 player_stat 레코드 내 필드 간 산술 불일치. 소스 API의 반올림 또는 집계 타이밍 차이.

---

## 5. match_stat shots_on_target 미수집 (40건)

| 체크명                                                                      | Entity    | 건수 | 현재 동작                                      |
|--------------------------------------------------------------------------|-----------|----|--------------------------------------------|
| `overall_stat_attack_shots_on_target == sum(match_stat shots_on_target)` | team-stat | 40 | team_stat에는 값 있으나, match_stat에서 모두 0 → 불일치 |

### 현상

40개 team-stat 전부 `actual=0`. match_stat 레코드 자체는 존재하지만, `shots_on_target` 필드가 0 또는 null. team_stat에는 정상 값이 있어 양쪽 데이터 모두
존재하지만 불일치.

### 원인

puller가 match_stat 레코드를 수집할 때 `shots_on_target` 필드를 채우지 않는 버그. Validator 로직은 정상 동작함.

### 조치

puller의 match_stat 수집 로직에서 `shots_on_target` 필드 매핑 확인 및 수정 필요.

---

## 6. Analytics vs 로컬 재계산 불일치 (8건)

| 체크명                                     | Entity    | 건수 |
|-----------------------------------------|-----------|----|
| `total_goals derived value`             | analytics | 1  |
| `total_red_cards derived value`         | analytics | 1  |
| `per_match_goals derived value`         | analytics | 1  |
| `per_match_yellow_cards derived value`  | analytics | 1  |
| `per_match_substitutions derived value` | analytics | 1  |
| `per_match_pass_accuracy derived value` | analytics | 2  |
| `delta derived value`                   | analytics | 1  |

### 현상

`analytics.value`는 소스 API에서 pull해 DB에 저장된 값. Validator는 로컬 `MatchEntity`/`MatchStatEntity`로 재계산해서 비교. 양쪽 모두 존재하지만 값이 다름.

예: `total_goals` analytics=819, 로컬 재계산=556

### 원인

analytics 테이블과 match 테이블이 **서로 다른 시점에 pull**됨. analytics pull 시점 기준으로는 특정 경기들이 이미 진행됐지만, match pull 시점에는 해당 경기들이 아직 수집되지
않았거나, 반대로 match가 먼저 pull된 경우도 가능. analytics는 "현재까지 진행된 경기" 기준으로 계산되므로 fixture_count와는 무관.

### 조치

두 테이블의 pull을 동일 시점에 수행하도록 pull 순서/일관성 관리 필요. 또는 analytics 저장 시 기준 match_count를 함께 저장하여 비교 가능성을 확보.

---

## 7. cumulative_points 배열 길이 불일치 (40건)

| 체크명                                           | Entity    | 건수 |
|-----------------------------------------------|-----------|----|
| `len(home_cumulative_points) == home_matches` | team-stat | 20 |
| `len(away_cumulative_points) == away_matches` | team-stat | 20 |

### 현상

패턴이 일관됨 — `home_matches=15`인데 `home_cumulative_points` 길이=30 (약 2배).

Validator는 다음 세 가지를 함께 체크함:

1. `len(home_cumulative_points) == home_matches`
2. `home_cumulative_points[-1] == home_points`
3. delta가 `{0, 1, 3}` 중 하나

### 원인

puller가 `home_cumulative_points`에 홈 경기만의 누적 포인트 배열이 아닌 **전체 경기(홈+원정) 누적 포인트 배열**을 저장하고 있는 것으로 추정. Validator 체크 자체는 정확함.

### 조치

puller에서 `home_cumulative_points` / `away_cumulative_points` 필드 매핑 확인. 소스 API 응답에서 홈/원정 구분된 배열을 올바르게 분리하여 저장해야 함.

---

## 요약

| # | 체크명                            | 건수      | 성격                              |
|---|--------------------------------|---------|---------------------------------|
| 1 | 골 이벤트 vs 스코어 불일치               | 125     | goal_association 데이터 품질         |
| 2 | 골 득점자 라인업 불일치                  | 66      | lineup vs goal event 동기화        |
| 3 | team_stat vs match_stat 집계 불일치 | 158     | 갱신 시점 차이 또는 집계 기준 차이            |
| 4 | 수비 듀얼 합산 불일치                   | 1       | 필드 간 산술 오류                      |
| 5 | match_stat shots_on_target 미수집 | 40      | puller 버그로 인한 필드 미수집            |
| 6 | analytics vs 로컬 재계산 불일치        | 8       | analytics/match 테이블 pull 시점 불일치 |
| 7 | cumulative_points 배열 길이 불일치    | 40      | puller가 홈/원정 배열을 잘못 저장          |
|   | **합계**                         | **438** |                                 |

> 전체 3,382 FAIL 중 **438건(13.0%)이 소스 데이터 문제**, 나머지 87.0%는 validator가 미pull 데이터를 적절히 처리하지 못해 발생한 문제.
