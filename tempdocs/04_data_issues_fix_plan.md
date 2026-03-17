# 소스 데이터 이슈 수정 계획

`02_data_issues.md` 분석을 바탕으로 한 파일별 수정 계획.
각 이슈에 대해 merger/syncer 수준에서 수정 가능한 것과 불가능한 것을 구분.

---

## 수정 가능성 요약

| # | 이슈 | 수정 가능 | 대상 |
|---|------|-----------|------|
| 1 | 골 이벤트 vs 스코어 불일치 | 불가 | 소스 API 데이터 품질 문제 |
| 2 | 골 득점자 라인업 불일치 | 불가 | 소스 API 데이터 품질 문제 |
| 3 | team_stat vs match_stat 집계 불일치 | 부분 | API 엔드포인트 간 정의 차이 — 조사 필요 |
| 4 | 수비 듀얼 합산 불일치 | 불가 | 소스 API 반올림 오류 |
| 5 | match_stat shots_on_target 미수집 | 가능 | merger/puller 필드 매핑 수정 |
| 6 | Analytics vs 로컬 재계산 불일치 | 가능 | syncer dependency 추가 |
| 7 | cumulative_points 배열 길이 불일치 | 가능 | merger 버그 수정 |

---

## 수정 불가 이슈 (1, 2, 4)

### 이슈 1: 골 이벤트 vs 스코어 불일치 (125건)
`goal_association` 레코드와 `match.score`는 소스 API의 서로 다른 엔드포인트에서 독립적으로 수집됨. 두 데이터 간 동기화는 API 제공자 측 문제. merger/syncer에서 수정 불가.

### 이슈 2: 골 득점자 라인업 불일치 (66건)
goal event의 `player_id`와 lineup의 `player_id`가 소스 API 내부에서 불일치. 구조적 문제로 merger/syncer에서 수정 불가.

### 이슈 4: 수비 듀얼 합산 불일치 (1건)
`defending_duels_won != aerial_won + ground_won` 차이 1건. 소스 API 반올림 또는 집계 타이밍 오차. 단일 레코드로 merger 수정 불가.

---

## 이슈 3: team_stat vs match_stat 집계 불일치 (158건) — 조사 필요

**구조**: `TeamStatMerger._apply_api_stats()`는 `v2_team_stat` API를 사용하고, `MatchStatMerger._build_entity()`는 `v1_match` API를 사용. 두 API 간 필드 정의/집계 범위 차이가 root cause.

| 체크 | team_stat 출처 | match_stat 출처 | 차이 원인 |
|------|---------------|-----------------|-----------|
| `total_shots` | `v2_team_stat.total_shots` | `v1_match.total_scoring_att` | 집계 범위 차이 가능성 |
| `blocks` | `v2_team_stat.blocked_shots` | `v1_match.outfielder_block` | 필드 정의 차이 가능성 |
| `tackles` | `v2_team_stat.times_tackled` | `v1_match.total_tackle` | 필드 정의 차이 가능성 |
| `corners` | `v2_team_stat.corners_taken_incl_short_corners` | `v1_match.corner_taken` | 숏코너 포함 여부 차이 |

**조치**: 각 API 엔드포인트의 실제 응답 필드 정의 확인 필요. `corners` 불일치는 `corners_taken_incl_short_corners` vs `corner_taken` 명칭에서 원인이 명확 — match_stat의 코너킥 집계에 숏코너 포함 여부 검토.

---

## 이슈 5: match_stat shots_on_target 미수집 (40건) — merger/puller 수정

**파일**: `merger/mergers/match_stat.py`, `puller/interfaces/pulselive/v1_match.py`

**현상**: `MatchStatEntity.shots_on_target` 값이 40개 match에서 전부 0.

**코드 추적**:
- `match_stat_merger.py` line 123: `shots_on_target=int(our.ontarget_scoring_att)`
- `v1_match.py` line 276: `ontarget_scoring_att: float = 0.0` (default=0.0)

**원인 후보**:
1. API 응답에 `ontarget_scoring_att` 키가 없어서 default 0.0으로 저장됨
2. API가 해당 경기들에 대해 실제로 0을 반환

**조사 방법**: 해당 40개 match의 raw API 응답에서 `ontarget_scoring_att` 필드 값 확인.

**수정 방안 A** (필드명이 다를 경우):
`v1_match.py` 인터페이스에서 올바른 필드명으로 수정.

**수정 방안 B** (default=0.0이 문제인 경우):
default를 `None`으로 변경하여 미수신 시 명시적으로 null 저장. validator 측에서도 None 처리.

```python
# v1_match.py 수정
ontarget_scoring_att: float | None = None  # 0.0 default 제거

# match_stat_merger.py 수정
shots_on_target=int(our.ontarget_scoring_att) if our.ontarget_scoring_att is not None else 0,
```

> **우선 조치**: 실제 API 응답 확인 후 수정 방향 결정. 40개 match가 특정 시즌/competition에 집중되어 있다면 API 엔드포인트 이슈일 가능성 높음.

---

## 이슈 6: Analytics vs 로컬 재계산 불일치 (8건) — syncer dependency 추가

**현상**: analytics 테이블과 match 테이블이 서로 다른 시점에 sync됨 → 불일치 발생.

**구조 파악**:
- `syncer/dependency.py`의 `DEPENDENCY_GRAPH`에 `ANALYTICS` 엔티티가 없음
- analytics는 `common/repositories/analytics/` 경로의 별도 모듈로 관리됨 (별도 syncer 존재 가능)

**조치 방향**:

### 6-1. analytics가 이 모듈에서 sync된다면

`DEPENDENCY_GRAPH`에 analytics 의존성 추가:

```python
# syncer/dependency.py 수정

class SyncEntity(StrEnum):
    # 기존 항목들...
    ANALYTICS = "analytics"  # 추가

DEPENDENCY_GRAPH: dict[SyncEntity, list[SyncEntity]] = {
    # 기존 항목들...
    SyncEntity.ANALYTICS: [SyncEntity.MATCH, SyncEntity.MATCH_STAT],  # 추가
}
```

이렇게 하면 analytics sync 시 반드시 match, match_stat이 먼저 sync됨.

### 6-2. analytics가 별도 외부 모듈에서 sync된다면

analytics sync 실행 전에 match/match_stat sync가 완료되도록 **실행 순서를 문서화하고 운영 절차에 반영**. 코드 수정 불가.

> **우선 조치**: analytics syncer의 위치 확인 후 6-1/6-2 중 해당하는 방향 적용.

---

## 이슈 7: cumulative_points 배열 길이 불일치 (40건) — merger 버그 수정

**파일**: `merger/mergers/team_stat.py`

**버그 위치**: `_apply_match_result()` lines 137-139

**현재 코드**:
```python
team_stat.overall_cumulative_points.append(team_stat.overall_points)
team_stat.home_cumulative_points.append(team_stat.home_points)   # ← 버그
team_stat.away_cumulative_points.append(team_stat.away_points)   # ← 버그
```

모든 match iteration에서 home/away 구분 없이 두 배열 모두에 append하기 때문에, 30경기 팀(홈15 + 원정15)의 `home_cumulative_points` 길이가 30이 됨.

**수정**: `is_home` 기준으로 분기하여 해당 배열에만 append.

```python
# merger/mergers/team_stat.py _apply_match_result() 수정

team_stat.overall_cumulative_points.append(team_stat.overall_points)
if is_home:
    team_stat.home_cumulative_points.append(team_stat.home_points)
else:
    team_stat.away_cumulative_points.append(team_stat.away_points)
```

**영향**: 기존에 잘못 저장된 레코드는 재sync 필요. `TeamStatSyncTask`는 기존 레코드에 대해 `_reset_derived_phase_1_fields()`를 호출하여 배열을 `[]`로 초기화 후 재계산하므로 (`team_stat_merger.py` line 50, 265, 275, 285), 재sync 시 자동 수정됨.

---

## 수정 파일 목록

| 파일 | 이슈 | 변경 내용 |
|------|------|-----------|
| `merger/mergers/team_stat.py` | 7 | `_apply_match_result()` 내 cumulative_points 조건부 append |
| `puller/interfaces/pulselive/v1_match.py` | 5 | `ontarget_scoring_att` default 또는 필드명 수정 (조사 후 결정) |
| `merger/mergers/match_stat.py` | 5 | `shots_on_target` None 처리 (필요 시) |
| `syncer/dependency.py` | 6 | `ANALYTICS` 엔티티 및 의존성 추가 (analytics syncer 위치 확인 후 결정) |
