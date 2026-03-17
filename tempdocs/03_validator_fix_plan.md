# Validator 수정 계획

`01_validator_issues.md` 분석을 바탕으로 한 파일별 구체 수정 계획.

---

## 수정 대상 파일 목록

| 파일 | 이슈 | 수정 항목 수 |
|------|------|-------------|
| `validator/validators/fixture.py` | A-1 | 2 |
| `validator/validators/season.py` | A-1, WARNING→SKIP | 3 |
| `validator/validators/player.py` | A-1, WARNING→SKIP | 2 |
| `validator/validators/player_stat.py` | A-1, B-2 | 3 |
| `validator/validators/match.py` | A-2 | 1 |
| `validator/cross_dataset.py` | WARNING→SKIP | 2 |

---

## 1. `fixture.py`

### 1-1. `home/away team registered for season` → SKIP (이슈 A-1)

**위치**: line 171-185

**현재**: `season_team_ids`가 빈 set이어도 체크 실행 → FAIL

**수정**:
```python
# line 171
season_team_ids = registrations.get(fixture.season_id, set())
if not season_team_ids:
    # Association 데이터 미pull — 등록 여부 검증 불가
    result.add_skip("home team registered for season", entity_id)
    result.add_skip("away team registered for season", entity_id)
else:
    self.check_true(
        result,
        "home team registered for season",
        fixture.home_team_id in season_team_ids,
        entity_id,
        detail=f"season_id={fixture.season_id}",
    )
    self.check_true(
        result,
        "away team registered for season",
        fixture.away_team_id in season_team_ids,
        entity_id,
        detail=f"season_id={fixture.season_id}",
    )
```

---

## 2. `season.py`

### 2-1. `has at least one fixture` → SKIP for future seasons (이슈 A-1)

**위치**: line 124-131

**현재**: fixture_count == 0 → 무조건 FAIL

**수정**: `season.date_start > now`인 미래 시즌은 fixture 미생성이 정상 → SKIP

```python
# 파일 상단에 추가
from football_data_manager.common.utils.type_helper.datetime_helper import create_utc_now

# validate() 메서드 시작부에 추가
now = create_utc_now()

# line 124 교체
fixture_count = fixture_count_by_season.get(season.id, 0)
if fixture_count > 0:
    result.add_pass("has at least one fixture", entity_id)
elif season.date_start > now:
    result.add_skip("has at least one fixture", entity_id)  # 미래 시즌
else:
    result.add_fail(
        "has at least one fixture",
        entity_id,
        detail="No Fixture records found for season",
    )
```

### 2-2. `registered team count reasonable` WARNING → SKIP (이슈 WARNING→SKIP)

**위치**: line 133-141

**현재**: `registered_teams=0`이면 WARNING

**수정**: Association 데이터가 없으면(0건) SKIP. 수집됐으나 범위를 벗어나면 기존 WARNING 유지.

```python
registered_team_ids = registered_team_ids_by_season.get(season.id, set())
if not registered_team_ids:
    result.add_skip("registered team count reasonable", entity_id)
elif 10 <= len(registered_team_ids) <= 30:
    result.add_pass("registered team count reasonable", entity_id)
else:
    result.add_warning(
        "registered team count reasonable",
        entity_id,
        detail=f"registered_teams={len(registered_team_ids)}",
    )
```

### 2-3. `fixture team set matches registered teams` WARNING → SKIP (이슈 WARNING→SKIP)

**위치**: line 143-153

**현재**: registered_team_ids가 비어 있어도 WARNING

**수정**: Association 데이터 없으면 SKIP

```python
if not registered_team_ids:
    result.add_skip("fixture team set matches registered teams", entity_id)
elif fixture_team_ids_by_season.get(season.id, set()) == registered_team_ids:
    result.add_pass("fixture team set matches registered teams", entity_id)
else:
    result.add_warning(
        "fixture team set matches registered teams",
        entity_id,
        detail=(
            f"fixture_teams={len(fixture_team_ids_by_season.get(season.id, set()))}, "
            f"registered_teams={len(registered_team_ids)}"
        ),
    )
```

---

## 3. `player.py`

### 3-1. `has PlayerChampionshipAssociation` → SKIP when no PCA data (이슈 A-1)

**위치**: line 117-139

**현재**: `associations == []`이면 무조건 FAIL — PCA 테이블이 통째로 미pull인 경우도 포함

**수정**: PCA 레코드가 DB에 전혀 없는 상태면 체크 자체를 SKIP

```python
# session 로드 구간에 추가 (players 로드 후)
any_pca_exists = bool(
    (
        await session.execute(
            select(PlayerChampionshipAssociation.player_id).limit(1)
        )
    ).first()
)

# 루프 내 line 117 교체
associations = list(player.championship_season_associations)
relevant_associations = [
    association
    for association in associations
    if not season_ids or association.season_id in season_ids
]
if not any_pca_exists:
    result.add_skip("has PlayerChampionshipAssociation", entity_id)
elif relevant_associations:
    result.add_pass("has PlayerChampionshipAssociation", entity_id)
elif associations and (season_id or competition_id):
    result.add_warning(
        "has PlayerChampionshipAssociation",
        entity_id,
        detail="Player exists but not in scoped seasons",
    )
else:
    result.add_fail(
        "has PlayerChampionshipAssociation",
        entity_id,
        detail="No PlayerChampionshipAssociation found",
    )
```

### 3-2. `PlayerStat exists for associated season` WARNING → SKIP (이슈 WARNING→SKIP)

**위치**: line 141-153

**현재**: `result.add_warning(...)` 출력

**수정**: 미pull 시즌은 검증 대상이 아니므로 출력 없이 SKIP

```python
for association in relevant_associations:
    if association.season_id in player_stat_seasons.get(player.id, set()):
        result.add_pass(
            "PlayerStat exists for associated season",
            entity_id,
            detail=f"season_id={association.season_id}",
        )
    # else: skip — 미pull 시즌 PlayerStat 부재는 검증 대상 아님
```

---

## 4. `player_stat.py`

### 4-1. `player registered in PlayerChampionshipAssociation` → SKIP when no PCA (이슈 A-1)

**위치**: line 418-425

**현재**: `player_season_memberships`가 비어 있으면 항상 FAIL

**수정**: 해당 season에 PCA 데이터가 없으면 SKIP

```python
# session 로드 구간에 추가: PCA가 존재하는 season_id 집합
seasons_with_pca: set[str] = {
    player_season_id
    for memberships in player_season_memberships.values()
    for player_season_id in memberships
}

# 루프 내 line 418 교체
if player_stat.season_id not in seasons_with_pca:
    result.add_skip("player registered in PlayerChampionshipAssociation", entity_id)
else:
    self.check_true(
        result,
        "player registered in PlayerChampionshipAssociation",
        player_stat.season_id in player_season_memberships.get(player_stat.player_id, set()),
        entity_id,
        detail=f"season_id={player_stat.season_id}",
    )
```

### 4-2. `team registered in TeamChampionshipAssociation` → SKIP when no TCA (이슈 A-1)

**위치**: line 426-432

**현재**: `team_season_memberships`가 비어 있으면 항상 FAIL

**수정**: 해당 season에 TCA 데이터가 없으면 SKIP

```python
# session 로드 구간에 추가: TCA가 존재하는 season_id 집합
seasons_with_tca: set[str] = {season_id_value for _, season_id_value in team_season_memberships}

# 루프 내 line 426 교체
if player_stat.season_id not in seasons_with_tca:
    result.add_skip("team registered in TeamChampionshipAssociation", entity_id)
else:
    self.check_true(
        result,
        "team registered in TeamChampionshipAssociation",
        (player_stat.team_id, player_stat.season_id) in team_season_memberships,
        entity_id,
        detail=f"season_id={player_stat.season_id}",
    )
```

### 4-3. `number >= 1` → 등번호 0 허용 (이슈 B-2)

**위치**: line 111-117

**현재**: `number=0`도 FAIL

**수정**: 0은 API의 미배정 값 → SKIP

```python
# line 111 교체
if player_stat.number is not None and player_stat.number > 0:
    self.check_true(
        result,
        "number >= 1",
        player_stat.number >= 1,
        entity_id,
        detail=f"number={player_stat.number}",
    )
# else: skip — 0은 API 미배정 값
```

---

## 5. `match.py`

### 5-1. Formation 체크에 `kickoff_time + clock < now` gate 추가 (이슈 A-2)

**위치**: line 134-147

**현재**: period 무관, 모든 match에 대해 formation 체크 실행

**수정**: `kickoff_time + clock`이 현재 시각보다 이른 경우에만 체크

```python
# 파일 상단 import 추가
from datetime import timedelta
from football_data_manager.common.utils.type_helper.datetime_helper import create_utc_now

# validate() 시작부에 추가
now = create_utc_now()

# line 134-147 교체 (기존 두 check_equal 대체)
fixture_value = fixture_map.get(match.fixture_id)
match_progressed = (
    fixture_value is not None
    and fixture_value.kickoff_time + timedelta(minutes=match.clock) < now
)
if match_progressed:
    self.check_equal(
        result,
        "home_team_formation sum == 10",
        sum(match.home_team_formation),
        10,
        entity_id,
    )
    self.check_equal(
        result,
        "away_team_formation sum == 10",
        sum(match.away_team_formation),
        10,
        entity_id,
    )
# else: skip — 경기 미시작 또는 kickoff 전
```

> **참고**: `match_progressed=True`이고 `formation=[]`이면 FAIL이 맞음 (데이터 이슈, `02_data_issues.md` 참조). 80건 중 실제로 몇 건이 이 케이스인지 수정 후 재검증 필요.

---

## 6. `cross_dataset.py`

### 6-1. `sum(team_stat.matches) == fixture_count * 2` WARNING → SKIP (이슈 WARNING→SKIP)

**위치**: line 139-151

**현재**: 불일치 시 WARNING

**수정**: Association 데이터가 없는 시즌(`team_count == 0`)은 SKIP

```python
# line 139 교체
if team_count == 0:
    result.add_skip("sum(team_stat.matches) == fixture_count * 2", entity_id)
elif total_matches == fixture_count * 2:
    result.add_pass("sum(team_stat.matches) == fixture_count * 2", entity_id)
else:
    result.add_warning(
        "sum(team_stat.matches) == fixture_count * 2",
        entity_id,
        detail=f"actual={total_matches}, expected={fixture_count * 2}",
    )
```

### 6-2. `fixture_count == team_count * (team_count - 1)` WARNING → SKIP (이슈 WARNING→SKIP)

**위치**: line 153-169

**현재**: `team_count <= 1`이면 WARNING

**수정**: `team_count == 0` (Association 미pull)이면 SKIP, `team_count == 1`은 기존 WARNING 유지

```python
# line 153 교체
if team_count == 0:
    result.add_skip("fixture_count == team_count * (team_count - 1)", entity_id)
elif team_count == 1:
    result.add_warning(
        "fixture_count == team_count * (team_count - 1)",
        entity_id,
        detail=f"Insufficient team registration data (team_count={team_count})",
    )
else:
    self.check_equal(
        result,
        "fixture_count == team_count * (team_count - 1)",
        fixture_count,
        team_count * (team_count - 1),
        entity_id,
    )
```

---

## 수정 후 예상 효과

| 이슈 | 현재 FAIL/WARNING | 수정 후 |
|------|-------------------|---------|
| A-1. Association 미pull (~2,622 FAIL) | FAIL | SKIP |
| A-2. Formation 미수집 (160 FAIL) | FAIL | SKIP (미진행 경기) / FAIL 유지 (진행 경기) |
| B-2. 등번호 0 (7 FAIL) | FAIL | SKIP |
| WARNING → SKIP (82 WARNING) | WARNING | SKIP |
| **합계** | **~2,871** | **→ 0** |

> A-2는 수정 후 재검증을 통해 "진행된 경기 + formation=[]" 케이스를 별도 집계하여 `02_data_issues.md`에 추가 필요.
