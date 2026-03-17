# Validator 문제

Validator가 수정되어야 하는 케이스. 크게 두 유형:
- **A. 미pull 데이터 미처리**: 데이터 레코드 자체가 pull되지 않았을 때 FAIL 대신 SKIP/PASS해야 함
- **B. 로직 버그**: Validator의 가정이나 계산이 잘못됨

---

## A. 미pull 데이터 미처리

### A-1. Association 데이터 미등록 시 모든 관련 체크 FAIL (~2,622건)

**근본 원인**: 특정 시즌의 `TeamChampionshipAssociation` / `PlayerChampionshipAssociation` 데이터가 pull되지 않았을 때, 해당 데이터에 의존하는 모든 체크가 무조건 FAIL 처리됨.

| 체크명 | Entity | 건수 | 현재 동작 |
|--------|--------|------|-----------|
| `player registered in PlayerChampionshipAssociation` | player-stat | 710 | `season_id in empty_set` → FAIL |
| `team registered in TeamChampionshipAssociation` | player-stat | 656 | `(team_id, season_id) in empty_set` → FAIL |
| `has PlayerChampionshipAssociation` | player | 461 | `associations == []` → FAIL |
| `home team registered for season` | fixture | 361 | `team_id in empty_set` → FAIL |
| `away team registered for season` | fixture | 361 | `team_id in empty_set` → FAIL |
| `has at least one fixture` | season | 73 | `fixture_count == 0` → FAIL |

**영향 시즌**:
- `85c2b6fa`: TeamChampionshipAssociation + PlayerChampionshipAssociation 모두 없음 (~1,680건)
- `6c37c00d`: 일부 PlayerChampionshipAssociation 없음 (~47건)
- 73개 시즌: fixture 데이터 없음 (미래 시즌 또는 미pull)

**수정 방안**: 각 validator에서 의존 데이터 존재 여부를 먼저 확인. 없으면 체크를 SKIP하거나 WARNING 처리.

```python
# 예시: fixture.py
season_team_ids = registrations.get(fixture.season_id, set())
if not season_team_ids:
    result.add_pass("home team registered for season", entity_id)  # 또는 skip
    return
# 기존 체크 수행
```

---

### A-2. Match formation 미수집 시 FAIL (160건)

| 체크명 | Entity | 건수 | 현재 동작 |
|--------|--------|------|-----------|
| `home_team_formation sum == 10` | match | 80 | `sum([]) == 0` → FAIL |
| `away_team_formation sum == 10` | match | 80 | `sum([]) == 0` → FAIL |

**현상**: 80개 경기에서 `formation=[]`. 현재 validator는 period 관계없이 모든 match에 대해 formation 체크를 실행함. 반면 lineup/goals/cards는 `period == FULLTIME`에서만 실행 — 불일치.

**판단 기준**: `fixture.kickoff_time + timedelta(minutes=match.clock)`이 현재 시각보다 이른지 여부로 formation 존재 여부를 판단해야 함.

| 조건 | formation=[] 의미 | 처리 |
|------|-------------------|------|
| `period == PREMATCH` 또는 kickoff 전 | 아직 경기 미시작 — 정상 | SKIP |
| `kickoff_time + clock < now` (경기 진행/완료) | 수집됐어야 하는 데이터 없음 | FAIL (데이터 이슈) |

**Validator 코드 문제**: formation 체크(line 134-147)가 period 조건 없이 실행됨. lineup 체크(line 235)와 동일하게 period 기반 또는 시간 기반 gate 추가 필요.

**수정 방안**: `kickoff_time + clock < now` 조건을 gate로 사용.

```python
fixture_value = fixture_map.get(match.fixture_id)
now = datetime.now(tz=timezone.utc)
match_progressed = (
    fixture_value is not None
    and fixture_value.kickoff_time + timedelta(minutes=match.clock) < now
)
if match_progressed:
    self.check_equal(result, "home_team_formation sum == 10", sum(match.home_team_formation), 10, entity_id)
    self.check_equal(result, "away_team_formation sum == 10", sum(match.away_team_formation), 10, entity_id)
# else: skip — 경기 미시작 또는 진행 전
```

> **분류 주의**: `match_progressed=True`인데 formation이 없으면 validator가 맞게 FAIL하는 것. 해당 케이스는 puller 문제로 `02_data_issues.md`에 별도 기록 필요. 80건 중 이 케이스가 몇 건인지 확인 후 분리 필요.

---

### A-3. ~~match_stat 집계 필드 미수집 시 FAIL~~ → 02_data_issues.md로 이동

> **이동**: match_stat 레코드는 존재하나 `shots_on_target` 필드가 0/null인 puller 버그. Validator 로직은 정상 동작하므로 validator 이슈 아님 → `02_data_issues.md` 5번 참조.

---

### A-4. ~~Analytics 파생값 검증 시 경기 데이터 미pull~~ → 02_data_issues.md로 이동

> **이동**: analytics.value(API pull 값)와 로컬 재계산값의 불일치는 두 테이블의 pull 시점/범위 불일치 문제. Validator 로직 자체는 정상이므로 validator 이슈 아님 → `02_data_issues.md` 6번 참조.

---

### A-5. ~~등번호 0 처리~~ → B-2로 재분류

> **재분류**: player_stat 레코드와 `number` 필드 모두 정상 수집됨. API가 미배정 시 0을 반환하는 것이므로 "미pull" 아닌 **Validator 로직 버그**. [B-2](#b-2-등번호-0-미배정-처리-오류-7건) 참조.

---

## B. 로직 버그

### B-1. ~~`cumulative_points` 길이 비교 오류~~ → 02_data_issues.md로 이동

> **이동**: Validator의 `len(home_cumulative_points) == home_matches` 체크는 정확함. 데이터가 잘못 수집된 것 → `02_data_issues.md` 7번 참조.

---

### B-2. 등번호 0 미배정 처리 오류 (7건)

| 체크명 | Entity | 건수 |
|--------|--------|------|
| `number >= 1` | player-stat | 7 |

**현상**: `number=0`인 player_stat 7건. 소스 API가 등번호 미배정 선수에 대해 0을 반환. player_stat 레코드와 `number` 필드 모두 정상 수집됨.

**원인**: Validator가 `number >= 1`만 허용하며, API의 0(미배정) 반환 패턴을 고려하지 않음.

**수정 방안**: 0은 "미배정"으로 취급하여 SKIP.

```python
if player_stat.number is not None and player_stat.number > 0:
    self.check_gte(result, "number >= 1", player_stat.number, 1, entity_id)
# else: skip (미배정 — API가 0 반환)
```

---

## WARNING 분류 → SKIP으로 전환 (82건)

미pull 데이터에 대해 현재 WARNING을 내보내고 있으나, **미pull 시즌은 검증 대상이 아니므로 WARNING도 출력하지 않도록** 수정.

| 체크명 | Entity | 건수 | 현재 처리 | 변경 후 |
|--------|--------|------|-----------|---------|
| `registered team count reasonable` | season | 74 | WARNING (registered_teams=0) | SKIP |
| `PlayerStat exists for associated season` | player | 6 | WARNING | SKIP |
| `sum(team_stat.matches) == fixture_count * 2` | cross-dataset | 1 | WARNING | SKIP |
| `fixture_count == team_count * (team_count - 1)` | cross-dataset | 1 | WARNING | SKIP |
| `fixture team set matches registered teams` | season | 1 | WARNING | SKIP |

**수정 방안**: 각 체크에서 의존 데이터(팀 등록 정보, fixture 등)가 존재하지 않으면 WARNING 없이 SKIP.

---

## 요약

| 유형 | 카테고리 | 건수 | 핵심 수정 |
|------|----------|------|-----------|
| A-1. Association 미pull | A. 미pull 데이터 | ~2,622 | 의존 데이터 존재 여부 선검증 |
| A-2. Formation 미수집 | A. 미pull 데이터 | 160 | kickoff+clock < now 조건 gate 추가; 진행된 경기 FAIL은 02_data_issues로 분리 필요 |
| WARNING → SKIP | A. 미pull 데이터 | 82 | 미pull 시즌 대상 WARNING 제거, SKIP으로 전환 |
| B-1. cumulative_points 길이 불일치 | → 02_data_issues.md | 40 | — |
| B-2. 등번호 0 미배정 처리 오류 | B. 로직 버그 | 7 | 0 → 미배정 SKIP |
| A-3. match_stat 필드 미수집 | → 02_data_issues.md | 40 | — |
| A-4. Analytics pull 시점 불일치 | → 02_data_issues.md | 8 | — |
| **합계 (validator 이슈)** | | **~2,829** | |
