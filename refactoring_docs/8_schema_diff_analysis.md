# Schema Diff Analysis: Entity 코드 vs 실제 DB

**상태**: Entity 코드 수정 완료 ✅ / DB 마이그레이션 대기 중 ⏳
**목적**: Phase 1 Entity 코드와 실제 DB 스키마 간 차이점 분석 및 해결 방향 결정
**선행 조건**: Phase 1 완료, Alembic stamp head 완료

> Alembic `--autogenerate` 결과 Entity 코드와 DB 사이에 7개 차이점이 발견되었습니다.
> 각 이슈별로 분석과 추천안을 제시합니다. **[YOUR_CHOICE]** 에 선택을 기입해주세요.

---

## 목차

1. [Issue 1: `metadata` 테이블](#issue-1-metadata-테이블)
2. [Issue 2: `teams` 테이블 - 미사용 컬럼 4개](#issue-2-teams-테이블---미사용-컬럼-4개)
3. [Issue 3: `teams.icon_url` nullable 불일치](#issue-3-teamsicon_url-nullable-불일치)
4. [Issue 4: `player_stats.minutes_played` nullable 불일치](#issue-4-player_statsminutes_played-nullable-불일치)
5. [Issue 5: `grounds.name_en` unique 제약 누락](#issue-5-groundsname_en-unique-제약-누락)
6. [Issue 6: `match_stats.match_id` FK 제약 누락](#issue-6-match_statsmatch_id-fk-제약-누락)
7. [Issue 7:
   `player_championship_association.player_id` FK 제약 누락](#issue-7-player_championship_associationplayer_id-fk-제약-누락)
8. [결정 후 실행 방법](#결정-후-실행-방법)

---

## Issue 1: `metadata` 테이블

### 현황

| 항목             | Entity 코드 | 실제 DB                        |
|----------------|-----------|------------------------------|
| `metadata` 테이블 | 없음        | 존재 (key, value, description) |

- archive 코드에도 `metadata`에 대한 Entity가 없음
- DB에만 남아 있는 테이블 (key-value 저장소 형태)

### Alembic이 하려는 것

```python
op.drop_table('metadata')
```

### 선택지

**A. DB에서 삭제** (추천)

- Entity 코드에 없으므로 Alembic 관리 대상이 아님
- 향후 autogenerate 실행할 때마다 diff로 잡힘
- 데이터가 있다면 삭제 전 백업 필요

**B. Alembic에서 무시 설정**

- `env.py`에 `include_name` 필터 추가하여 `metadata` 테이블을 autogenerate에서 제외
- DB에 테이블은 유지하되 Alembic이 관리하지 않음

**C. Entity 추가**

- `MetadataEntity` 클래스를 새로 정의
- 실제로 사용 계획이 있을 때만 의미 있음

**[YOUR_CHOICE]**: B 무시하겠습니다.

---

## Issue 2: `teams` 테이블 - 미사용 컬럼 4개

### 현황

| 컬럼                | Entity 코드 | 실제 DB             |
|-------------------|-----------|-------------------|
| `description_kr`  | 없음        | VARCHAR, nullable |
| `description_en`  | 없음        | VARCHAR, nullable |
| `color_primary`   | 없음        | VARCHAR, nullable |
| `color_secondary` | 없음        | VARCHAR, nullable |

- archive 코드에도 이 4개 컬럼에 대한 정의 없음 (과거에 제거된 것으로 추정)
- DB에만 남아 있는 레거시 컬럼

### Alembic이 하려는 것

```python
op.drop_column('teams', 'description_kr')
op.drop_column('teams', 'color_primary')
op.drop_column('teams', 'description_en')
op.drop_column('teams', 'color_secondary')
```

### 선택지

**A. DB에서 컬럼 삭제** (추천)

- Entity에도 archive에도 없는 컬럼
- 향후 diff에 계속 잡힘
- 모두 nullable이므로 데이터가 비어있을 가능성 높음

**B. Entity에 컬럼 추가**

- `teams.py`에 4개 optional 컬럼 추가
- 향후 실제 사용 계획이 있을 때만 의미 있음

**C. Alembic에서 무시 설정**

- DB에 유지하되 Alembic이 관리하지 않음

**[YOUR_CHOICE]**: B 추가합니다.

---

## Issue 3: `teams.icon_url` nullable 불일치

### 현황

| 항목         | Entity 코드                   | 실제 DB              |
|------------|-----------------------------|--------------------|
| `icon_url` | `nullable=False` (NOT NULL) | nullable (NULL 허용) |

- Entity 정의: `icon_url: Mapped[str] = mapped_column(String, nullable=False)`
- 하지만 `__init__`에서: `icon_url: str | None = None` (기본값 None)
- **모순**: 컬럼은 NOT NULL인데 생성자는 None을 허용

### Alembic이 하려는 것

```python
op.alter_column('teams', 'icon_url',
                existing_type=sa.VARCHAR(),
                nullable=False)
```

### 선택지

**A. Entity를 nullable로 변경** (추천)

- `icon_url: Mapped[str | None] = mapped_column(String, nullable=True)`
- DB 현재 상태와 일치, 기존 데이터에 NULL이 있을 수 있음
- `__init__` 기본값 `None`과도 일관성 유지

**B. DB를 NOT NULL로 변경**

- 기존 데이터에 NULL이 없어야 함 (확인 필요)
- NULL 데이터가 있으면 마이그레이션 실패

**[YOUR_CHOICE]**: B 변경합니다.

---

## Issue 4: `player_stats.minutes_played` nullable 불일치

### 현황

| 항목               | Entity 코드                 | 실제 DB                |
|------------------|---------------------------|----------------------|
| `minutes_played` | `nullable=True` (NULL 허용) | NOT NULL (default 0) |

- Entity 정의: `minutes_played: Mapped[int | None] = mapped_column(Integer, nullable=True)`
- DB: NOT NULL with server default 0

### Alembic이 하려는 것

```python
op.alter_column('player_stats', 'minutes_played',
                existing_type=sa.INTEGER(),
                nullable=True,
                existing_server_default=sa.text('0'))
```

### 선택지

**A. Entity를 NOT NULL + default 0으로 변경** (추천)

- `minutes_played: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")`
- DB 현재 상태와 일치
- 의미적으로도 출장 시간 0은 NULL보다 명확

**B. DB를 nullable로 변경**

- Entity 현재 코드와 일치
- 기존 데이터의 default 0 값이 유지됨 (삭제되지 않음)

**[YOUR_CHOICE]**: A로 하겠습니다.

---

## Issue 5: `grounds.name_en` unique 제약 누락

### 현황

| 항목               | Entity 코드     | 실제 DB        |
|------------------|---------------|--------------|
| `name_en` unique | `unique=True` | unique 제약 없음 |

- Entity 정의: `name_en: Mapped[str] = mapped_column(String, nullable=False, unique=True)`
- `get_source_id()`가 `name_en` 기반으로 해시 생성 → name_en이 사실상 고유 식별자

### Alembic이 하려는 것

```python
op.create_unique_constraint(None, 'grounds', ['name_en'])
```

### 선택지

**A. DB에 unique 제약 추가** (추천)

- Entity 설계 의도와 일치 (name_en이 source_id 생성 기준)
- 데이터 무결성 강화
- 기존 데이터에 중복이 없어야 함 (확인 필요)

**B. Entity에서 unique 제거**

- `unique=True` 삭제
- DB 현재 상태 유지

**[YOUR_CHOICE]**: A로 하겠습니다.

---

## Issue 6: `match_stats.match_id` FK 제약 누락

### 현황

| 항목            | Entity 코드                                                             | 실제 DB             |
|---------------|-----------------------------------------------------------------------|-------------------|
| `match_id` FK | `ForeignKey(MatchEntity.id, ondelete="CASCADE", onupdate="RESTRICT")` | FK 제약 없음 (컬럼만 존재) |

- Entity에 FK 정의가 있지만 DB에는 컬럼만 있고 FK 제약이 없음
- 데이터 무결성이 DB 수준에서 보장되지 않는 상태

### Alembic이 하려는 것

```python
op.create_foreign_key(None, 'match_stats', 'matches', ['match_id'], ['id'],
                      onupdate='RESTRICT', ondelete='CASCADE')
```

### 선택지

**A. DB에 FK 제약 추가** (추천)

- 데이터 무결성 보장 (존재하지 않는 match 참조 방지)
- Entity 설계 의도와 일치
- 기존 데이터에 orphan 레코드가 없어야 함 (확인 필요)

**B. Entity에서 FK 제거**

- `ForeignKey(...)` 삭제, 일반 String 컬럼으로 변경
- DB 현재 상태 유지, 무결성은 애플리케이션 레벨에서 관리

**[YOUR_CHOICE]**: A로 하겠습니다.

---

## Issue 7: `player_championship_association.player_id` FK 제약 누락

### 현황

| 항목             | Entity 코드                                                              | 실제 DB             |
|----------------|------------------------------------------------------------------------|-------------------|
| `player_id` FK | `ForeignKey(PlayerEntity.id, ondelete="CASCADE", onupdate="RESTRICT")` | FK 제약 없음 (컬럼만 존재) |

- Issue 6과 동일한 패턴
- Association 테이블의 PK 일부이면서 FK가 걸려있어야 하는 컬럼

### Alembic이 하려는 것

```python
op.create_foreign_key(None, 'player_championship_association', 'players',
                      ['player_id'], ['id'],
                      onupdate='RESTRICT', ondelete='CASCADE')
```

### 선택지

**A. DB에 FK 제약 추가** (추천)

- 데이터 무결성 보장
- Entity 설계 의도와 일치
- Association 테이블은 FK가 있는 것이 표준 패턴

**B. Entity에서 FK 제거**

- DB 현재 상태 유지

**[YOUR_CHOICE]**: A로 하겠습니다.

---

## 적용 결과

### 완료된 코드 변경 (Entity 수정 + Alembic 설정)

| Issue | 작업 내용 | 상태 |
|-------|----------|------|
| Issue 1 | `env.py`에 `include_name` 필터 추가 → `metadata` 테이블 무시 | ✅ 완료 |
| Issue 2 | `teams.py`에 4개 optional 컬럼 추가 (`description_kr/en`, `color_primary/secondary`) | ✅ 완료 |
| Issue 3 | `teams.py` `__init__`에서 `icon_url`을 required 파라미터로 변경 (NOT NULL 일관성) | ✅ 완료 |
| Issue 4 | `player_stats.py` `minutes_played`를 `NOT NULL + server_default="0"`으로 변경 | ✅ 완료 |

### DB 마이그레이션 필요 (사용자 실행)

| Issue | 마이그레이션 내용 | 사전 확인 |
|-------|----------------|----------|
| Issue 3 | `teams.icon_url` → NOT NULL 변경 | `SELECT COUNT(*) FROM teams WHERE icon_url IS NULL;` 결과 0이어야 함 |
| Issue 5 | `grounds.name_en` → UNIQUE 제약 추가 | `SELECT name_en, COUNT(*) FROM grounds GROUP BY name_en HAVING COUNT(*) > 1;` 결과 없어야 함 |
| Issue 6 | `match_stats.match_id` → FK 제약 추가 | `SELECT ms.match_id FROM match_stats ms LEFT JOIN matches m ON ms.match_id = m.id WHERE m.id IS NULL;` 결과 없어야 함 |
| Issue 7 | `player_championship_association.player_id` → FK 제약 추가 | `SELECT pca.player_id FROM player_championship_association pca LEFT JOIN players p ON pca.player_id = p.id WHERE p.id IS NULL;` 결과 없어야 함 |

### 실행 순서

```bash
# 1. 위 4개 SQL 쿼리로 데이터 무결성 확인 (DB 클라이언트에서 실행)

# 2. 마이그레이션 생성
alembic revision --autogenerate -m "sync_schema_diff"

# 3. 생성된 마이그레이션 파일 검토 (Issue 3, 5, 6, 7만 포함되어야 함)

# 4. 마이그레이션 적용
alembic upgrade head
```

---

*문서 생성일: 2026-02-02*
*코드 변경 적용일: 2026-02-02*
