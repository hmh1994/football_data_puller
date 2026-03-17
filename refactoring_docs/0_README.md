# Refactoring Documentation

이 디렉토리는 Football Data Puller 프로젝트의 리팩토링 계획 및 실행 문서를 담고 있습니다.

**📖 읽기 순서**: 파일명 앞의 번호 순서대로 읽으세요 (0 → 1 → 2 → 3 → ...)

---

## 📚 문서 목록 (읽기 순서)

### 0. **`0_README.md`** (이 문서)

**목적**: 문서 네비게이션 및 읽기 가이드

---

### 1. **`1_master_plan.md`** (필수 읽기, 20분)

**목적**: 전체 리팩토링 계획 및 아키텍처 설계

**내용**:

- 6개 컴포넌트 구조 (Repository, Puller, Merger, Data Syncer, Data Validator, Scheduler)
- 목표 아키텍처 및 디렉토리 구조
- 기술 스택 결정 (모두 확정됨)
- Phase별 마이그레이션 전략
- 성공 기준 및 리스크 평가

**언제 읽나요**:

- 리팩토링 시작 전 전체 계획 파악
- 각 Phase 시작 전 해당 섹션 재확인

---

### 2. **`2_current_state_analysis.md`** (참고 자료, 선택, 30분)

**목적**: 현재 코드베이스의 상세 구조 분석

**내용**:

- 전체 디렉토리 구조 맵
- 15개 Entity + 15개 Repository 상세
- 11개 Association 테이블
- 20개 Puller 서비스 구조
- 아키텍처 패턴 및 설계 패턴
- 파일 분포 통계

**언제 읽나요**:

- 현재 구조를 상세히 파악하고 싶을 때
- 리팩토링 중 기존 패턴 참고 필요 시
- 새로운 팀원 온보딩

**특징**:

- 매우 상세한 분석 (60KB)
- 코드 예제 포함
- 통계 및 메트릭

---

### 3. **`3_calculation_formulas_reference.md`** (핵심 참고 자료, 보관용)

**목적**: 모든 점수 및 계산식 완전 문서화

**내용**:

- **Player Stat Scores (6개)**:
  - Shooting, Passing, Defending (Outfield/GK), Dribbling, Discipline, Overall
  - Prior 값 계산 (per90, ratio, GK 전용)
  - Bayesian shrinkage 공식 및 상수
  - 포지션별 가중치 테이블
- **Team Momentum Index**:
  - ΔPPM, ΔxG 기반 z-score 정규화
  - `tanh` 함수 기반 momentum 계산
- **Season Analytics (7개 메트릭)**:
  - Per-match: Goals, Pass Accuracy, Substitutions, xG, Yellow Cards
  - Total: Goals, Red Cards
  - Delta 계산 (이전 시즌 대비)
- **Utility Functions**:
  - `shrink_per90()`, `shrink_ratio()`, `featurize()`, `score100()`
  - Z-score normalization, `clamp()`, `tanh()`

**언제 읽나요**:

- 점수 계산 로직 수정 시
- 리팩토링 중 기존 로직 보존 필요 시
- 새로운 점수 필드 추가 시
- Momentum 또는 Analytics 계산 이해 필요 시

**⚠️ 중요**:

- **리팩토링 중 절대 유실되면 안 되는 문서**
- 모든 공식, 가중치, 상수는 검증된 값임
- 변경 시 반드시 이 문서 업데이트 필요

---

### 4. **`4_combined_migration_plan.md`** (Phase 0 전 실행 가이드, 15분 + 2-3시간 실행)

**목적**: Legacy Script 정리 + app.py 통합 CLI 구현

**내용**:

- **Step 0-4**: 복사-붙여넣기 가능한 실행 명령어
- **Step 2.3**: app.py 통합 CLI 구현 (핵심)
  - argparse 기반 CLI 구조
  - health, run, pull-data 명령어
  - Phase 2-4에서 구현할 TODO 포함
- Legacy scripts 아카이브 (`a.py`, `b.py`, `c.py` → `archive/legacy_scripts/`)
- Git 스냅샷 및 백업 전략
- 검증 체크포인트 포함

**언제 읽나요**:

- **Phase 0 시작 전 반드시 실행** (준비 작업)
- Root 디렉토리 정리 필요 시
- app.py CLI 구조 확인 필요 시

**⚠️ 중요**:

- Phase 0 (Alembic, pytest) 전에 먼저 실행
- **app.py 구현이 포함되어 실행 가능한 상태로 준비**
- 모든 백업 및 Git 스냅샷 포함
- 실행 완료 후 Phase 0 진행

---

### 5. **`5_phase_0_preparation.md`** (Phase 0 실행 가이드, 10분 + 2-3일 실행)

**목적**: Phase 0 준비 단계 실행 가이드 (Alembic 설정 전용)

**내용**:

- Alembic 설정 (step-by-step)
- alembic.ini 구성
- env.py에서 ConfigService 통합
- 검증 체크리스트
- 트러블슈팅 가이드

**언제 읽나요**:

- Phase 0 시작 시 (리팩토링 전 준비)
- Alembic 설정 시 참고

**특징**:

- 복사-붙여넣기 가능한 코드
- 실행 가능한 bash 명령어
- 단계별 검증 방법

**⚠️ 중요**:

- Phase 0는 **Alembic 설정만** 포함 (마이그레이션 생성/실행 제외)
- 마이그레이션 생성은 Phase 1+에서 필요 시 수행
- 데이터베이스 백업은 이 프로젝트에서 필요 없음

---

### 6. **`6_ai_agnostic_migration_plan.md`** (완료된 참고 문서, 선택, 15분)

**목적**: 문서 구조 개선의 설계 결정 기록 (이미 완료됨)

**내용**:

- `claudedocs/` → `refactoring_docs/` 이동 완료
- 파일 번호 체계 (0-6) 완료
- AI 중립적 문서 작성 가이드라인
- 설계 의도 및 결정 사항

**언제 읽나요**:

- **설계 의도 이해** 필요 시
- 왜 이런 문서 구조로 정리되었는지 궁금할 때

**⚠️ 상태**:

- ✅ **이미 완료됨** (2026-01-26)
- 실행할 것 없음 (참고용)

---

### 7. **`7_phase_1_repository.md`** (Phase 1 실행 가이드 - ✅ 완료)

**목적**: Repository 컴포넌트 전면 재구성 실행 가이드

**내용**:

- Step 1-10: 단계별 실행 가이드
- 초기 Alembic 마이그레이션
- 디렉토리 구조 생성 (`repository/entities/`, `repository/repositories/`)
- SQLAlchemy 2.0 스타일 적용 (`DeclarativeBase`, `Mapped[T]`)
- Entity 마이그레이션 (15 entities + 11 associations)
- AsyncBaseRepository 구현
- 개별 Repository 구현 (특수 메서드 보존)
- SessionFactory, RepositoryContainer (DI)
- 검증 체크리스트 및 트러블슈팅

**언제 읽나요**:

- Repository 구조 이해 필요 시

**특징**:

- 코드 예제 포함
- 파일 매핑 테이블
- archive 참조 경로 목록

---

### 8. **`8_schema_diff_analysis.md`** (Entity vs DB 스키마 차이 분석 - Entity 수정 ✅ / DB 마이그레이션 ⏳)

**목적**: Phase 1 Entity 코드와 실제 DB 스키마 간 7개 차이점 분석 및 해결 방향 결정

**내용**:

- 7개 이슈 분석 (테이블, 컬럼, nullable, FK, unique 제약)
- 각 이슈별 추천안 및 선택지 제시
- 적용 결과 및 DB 마이그레이션 실행 가이드

**현재 상태**:

- ✅ Issue 1: `env.py` `include_name` 필터 추가 (metadata 테이블 무시)
- ✅ Issue 2: `teams.py` 4개 optional 컬럼 추가
- ✅ Issue 3: `teams.py` `__init__` icon_url required로 변경
- ✅ Issue 4: `player_stats.py` minutes_played NOT NULL + server_default 변경
- ⏳ Issue 3, 5, 6, 7: DB 마이그레이션 적용 대기 중

**언제 읽나요**:

- Phase 1 완료 후, Alembic 마이그레이션 적용 전
- DB 스키마 정합성 확인 필요 시

---

### 9. **`9_phase_2_puller.md`** (Phase 2 실행 가이드)

**목적**: Puller 컴포넌트 전면 재구성 실행 가이드

**내용**:

- Step 1-11: 단계별 실행 가이드
- 디렉토리 구조 생성 (`puller/interfaces/`, `puller/clients/`, `puller/pullers/`)
- CamelCaseModel 마이그레이션
- Pulselive Interface 마이그레이션 (50 → ~12 파일 통합)
- The Athletic Interface 마이그레이션
- HTTP Client (Pulselive) + GraphQL Client (The Athletic) 구현
- AbstractPuller + 10 Pulselive Pullers + 1 The Athletic Puller 구현
- PullerContainer (DI) 구현
- 검증 체크리스트

**언제 읽나요**:

- Phase 2 시작 시
- Puller 구조 이해 필요 시

**특징**:

- 코드 예제 포함
- Archive 참조 경로 목록
- Phase 3 분리 지점 명시 (Puller vs Merger 역할)

---

### 10. **`10_interface_restructure.md`** (Interface 구조 변경 기록)

**목적**: Phase 2 Interface 파일 구조 변경 사항 기록

**언제 읽나요**:

- Interface 파일 구조 이해 필요 시

---

### 11. **`11_phase_3_merger.md`** (Phase 3 실행 가이드 - 🚧 진행 중)

**목적**: Merger 컴포넌트 전면 구현 실행 가이드

**내용**:

- Step 1-16: 단계별 실행 가이드
- 공통 서비스 구현 (TranslatorService, ResourceValidationClient)
- 11개 Merger 구현 (Competition → Season → Team → Player → Fixture → Match → MatchStat → PlayerStat → TeamStat → Award → News)
- PlayerStatScorer 구현 (6개 카테고리 점수 계산)
- MergerContainer (DI) 구현
- 전체 필드 매핑 테이블 (API → Entity)
- Association 테이블 관리 가이드
- 검증 체크리스트

**언제 읽나요**:

- Phase 3 시작 시
- Merger 구조 이해 필요 시

**특징**:

- 모든 Merger의 API → Entity 필드 매핑 테이블 포함
- Archive 참조 경로 목록
- Merger별 복잡도 및 구현 순서 명시
- 점수 계산 공식 참조 (`3_calculation_formulas_reference.md`)

---

### 12. **`12_phase_4_data_syncer.md`** (Phase 4 실행 가이드 - 🚧 진행 중)

**목적**: Data Syncer 컴포넌트 구현 실행 가이드

**내용**:

- 데이터 종속성 DAG (Directed Acyclic Graph) 설계
- DependencyResolver (위상 정렬 기반 자동 종속성 해결)
- 11개 SyncTask 구현 (Competition → Season → Team → Player → Fixture → Match → MatchStat → PlayerStat → TeamStat → Award → News)
- SyncOrchestrator (종속성 순서 실행 + 에러 핸들링)
- SyncContainer (DI) 구현
- `app.py` sync 명령어 추가 가이드
- 실행 결과 요약 출력 형식
- 검증 체크리스트

**언제 읽나요**:

- Phase 4 시작 시
- Sync 파이프라인 구조 이해 필요 시

**특징**:

- 종속성 그래프 및 위상 정렬 알고리즘 설명
- 11개 entity별 종속성 자동 해결 체인 테이블
- CLI 명령어 인터페이스 설계
- 전체 코드 예제 포함

---

### 13. **`13_phase_5_data_validator.md`** (Phase 5 실행 가이드 - ⏳ 대기 중)

**목적**: Data Validator 컴포넌트 구현 실행 가이드

**내용**:

- Step 1-8: 단계별 실행 가이드
- 디렉토리 구조 생성 (`validator/validators/`)
- 검증 결과 모델 (CheckLevel, ValidationCheck, ValidationResult)
- AbstractValidator + 11개 개별 Validator + CrossDatasetValidator 구현
- ValidationOrchestrator (전체/개별 검증 실행 + 리포트 출력)
- ValidatorContainer (팩토리 패턴)
- `app.py validate` 명령어 추가 가이드
- 검증 체크리스트

**언제 읽나요**:

- Phase 5 시작 시
- Validation 구조 이해 필요 시

**특징**:

- `0_README.md` Phase 5 섹션(5-1 ~ 5-12)의 검증 규칙 전체 참조
- 코드 예제 포함 (TeamStatValidator, MatchValidator 패턴)
- CLI 사용 예시
- 약 214개 검증 규칙 요약 테이블

---

## 🚀 빠른 시작

### **Phase 0 전 필수 작업** (Combined Migration)

```bash
# 통합 마이그레이션 계획 실행 (2-3시간)
cat refactoring_docs/4_combined_migration_plan.md

# Step 0: 백업 생성
git tag -a pre-migration/combined-2026-01-26 -m "Snapshot before migration"

# Step 1-4: 단계별 실행 (문서 참조)
# ...

# 완료 후 Phase 0 시작
```

**완료 기준**:

- [x] **app.py 통합 CLI 구현 완료** (Step 2.3) — 2026-02-01
- [x] Legacy scripts → `archive/legacy_scripts/` 이동 완료 — 2026-02-01
- [x] Root 디렉토리 정리 완료 (a.py, b.py, c.py 제거) — 2026-02-01
- [x] Git 스냅샷 생성 완료 (`pre-migration/legacy-scripts-2026-01-26` tag) — 2026-02-01

---

## 🚀 빠른 시작 (Phase 0)

### Step 1: 전체 계획 파악

```bash
# Master Plan 읽기 (20분)
cat refactoring_docs/1_master_plan.md
```

**핵심 확인사항**:

- [ ] 6개 컴포넌트 이해 (Repository, Puller, Merger, Data Syncer, Data Validator, Scheduler)
- [ ] 목표 디렉토리 구조 확인
- [ ] Phase별 일정 확인 (총 6-8주 예상)

### Step 2: Phase 0 준비 시작

```bash
# Phase 0 가이드 읽기 (10분)
cat refactoring_docs/5_phase_0_preparation.md

# Alembic 설정 시작
alembic init football_data_manager/migrations
```

**Phase 0 완료 기준**:

- [x] Alembic 설치 완료 (1.18.3)
- [x] alembic.ini 설정 완료 (프로젝트 루트)
- [x] env.py에서 ConfigService 통합 완료
- [x] Alembic이 DB 설정을 읽을 수 있는지 검증 완료

### Step 3: (필요 시) 상세 구조 참고

```bash
# 현재 구조 상세 분석 보기
cat refactoring_docs/2_current_state_analysis.md
```

---

## 📋 Phase 진행 상황

### Pre-Phase 0: Combined Migration - ✅ **완료** (2026-02-01)

- [x] app.py 통합 CLI 구현
- [x] Legacy scripts 아카이브 (a.py, b.py, c.py → `archive/legacy_scripts/`)
- [x] `football_data_manager/` 아카이브 (`archive/football_data_manager/`)
- [x] Root 디렉토리 정리
- [x] Git 스냅샷 및 bundle 백업

### Phase 0: Preparation - ✅ **완료** (2026-02-01)

- [x] Alembic 설정 (`alembic.ini`, `env.py`, 26개 테이블 등록)
- [x] `football_data_manager/` 최소 구조 생성 (entity/association 복원)
- [x] Repository 파일 제거 (재구성 방해 방지)
- [x] Entity 비즈니스 로직 메서드 제거 (스키마 정의만 유지)
- [x] Entity docstring 점검 및 수정

### Phase 1: Repository 리팩토링 - ✅ **완료** (2026-02-02) → `7_phase_1_repository.md`

- [x] 디렉토리 구조 생성 (`repository/entities/`, `repository/repositories/`)
- [x] Entity 마이그레이션 (SQLAlchemy 2.0, `Mapped[T]`, 15 entities)
- [x] Association 분리 (11 associations → 개별 파일)
- [x] AsyncBaseRepository + PulseliveRepository 구현
- [x] 개별 Repository 구현 (15 repositories, 특수 메서드 포함)
- [x] SessionFactory + RepositoryContainer (17 providers)
- [x] Alembic env.py 업데이트 (26 테이블 등록)

### Schema Diff 해결 - **진행 중** → `8_schema_diff_analysis.md`

- [x] Entity 코드 수정 (teams.py 4컬럼 추가, player_stats.py minutes_played 변경)
- [x] Alembic 무시 설정 (metadata 테이블)
- [ ] DB 데이터 무결성 확인 (4개 SQL 쿼리)
- [ ] Alembic 마이그레이션 생성 및 적용 (icon_url NOT NULL, grounds unique, 2개 FK)

### Phase 2: Puller 리팩토링 - ✅ **완료** (2026-02-23) → `9_phase_2_puller.md`

- [x] 디렉토리 구조 생성 (`puller/interfaces/`, `puller/clients/`, `puller/pullers/`)
- [x] CamelCaseModel + RawResponseModel + Interface 마이그레이션 (API 버전별 분리)
- [x] HTTP Client (Pulselive) + GraphQL Client (The Athletic) 구현
- [x] AbstractPuller + 10 Pulselive Pullers + 1 The Athletic Puller 구현
- [x] PullerContainer 구현 (14 providers)

### Phase 3: Merger 구현 - 🚧 **핵심 구현 완료, 통합 테스트 제외 검증 완료** (2026-02-23) → `11_phase_3_merger.md`

- [x] 디렉토리 구조 생성 (`merger/services/`, `merger/mergers/`)
- [x] 공통 서비스 구현 (TranslatorService, ResourceValidationClient)
- [x] 11개 Merger 구현 (Competition, Season, Team, Player, Fixture, Match, MatchStat, PlayerStat, TeamStat, Award, News)
- [x] PlayerStatScorer 구현 (6개 카테고리 점수 계산)
- [x] MergerContainer 구현 (17 providers)
- [x] 단위 테스트/회귀 검증 확장 (`pytest` 30 passed)
- [x] archive 필드 매핑 parity 검증 완료 (`tests/merger/test_phase3_archive_parity.py`)
- [ ] 통합 테스트 (단위 테스트/pytest 검증 완료)

### Phase 4: Data Syncer 구현 - 🚧 **핵심 구현 완료, 통합 검증 대기** (2026-02-23) → `12_phase_4_data_syncer.md`

> 📖 상세 실행 가이드: [`12_phase_4_data_syncer.md`](12_phase_4_data_syncer.md)

`app.py`에 데이터 동기화 명령어를 추가합니다. 입력된 파라미터(competition ID, season ID 등)에 해당하는 데이터만 선택적으로 Pull → Merge하여 DB를 갱신합니다.

- [x] `app.py`에 `sync` 명령어 추가 (argparse subcommand)
- [x] 대상별 sync 하위 명령어 구현 (competition, season, team, player, fixture, match, match-stat, player-stat, team-stat, award, news)
- [x] 입력 파라미터 설계 (`--competition-id`, `--season-id`, `--team-id` 등 필수/선택 조합)
- [x] 의존성 순서 자동 해결 (예: team sync 시 competition, season이 먼저 존재해야 함)
- [x] DI Container 초기화 → Puller pull → Merger merge 파이프라인 연결
- [x] async 진입점 (`asyncio.run`) 처리
- [x] 실행 결과 요약 출력 (생성/갱신/스킵 건수)
- [x] 에러 핸들링 (종속 실패 skip + 독립 task 계속 진행)
- [ ] 세션 롤백 전략 실증 (통합 시나리오 검증)
- [ ] 통합 테스트 (실제 API 호출 → DB 반영 확인)

### Phase 5: Data Validator 구현 - **대기 중** → `13_phase_5_data_validator.md`

> 📖 상세 실행 가이드: [`13_phase_5_data_validator.md`](13_phase_5_data_validator.md)

`app.py`에 데이터 교차 검증 명령어를 추가합니다. 특정 데이터셋을 선택하면 관련 데이터셋 간의 정합성을 검증합니다.

- [ ] `app.py`에 `validate` 명령어 추가 (argparse subcommand)
- [ ] 대상별 validate 하위 명령어 구현 (team-stat, player-stat, match, match-stat, fixture, season, competition, player, analytics, news, award)
- [ ] 검증 결과 리포트 출력 (PASS/FAIL/WARNING 항목별, 요약 + 상세)
- [ ] 통합 테스트

#### 5-1. TeamStat 검증

**자체 정합성 (단일 entity 내 필드 간 관계)**

- [ ] `overall_matches` == `overall_matches_won` + `overall_matches_drawn` + `overall_matches_lost`
- [ ] `home_matches` == `home_matches_won` + `home_matches_drawn` + `home_matches_lost`
- [ ] `away_matches` == `away_matches_won` + `away_matches_drawn` + `away_matches_lost`
- [ ] `overall_matches` == `home_matches` + `away_matches`
- [ ] `overall_matches_won` == `home_matches_won` + `away_matches_won`
- [ ] `overall_matches_drawn` == `home_matches_drawn` + `away_matches_drawn`
- [ ] `overall_matches_lost` == `home_matches_lost` + `away_matches_lost`
- [ ] `overall_goals_for` == `home_goals_for` + `away_goals_for`
- [ ] `overall_goals_against` == `home_goals_against` + `away_goals_against`
- [ ] `overall_goals_difference` == `overall_goals_for` - `overall_goals_against`
- [ ] `home_goals_difference` == `home_goals_for` - `home_goals_against`
- [ ] `away_goals_difference` == `away_goals_for` - `away_goals_against`
- [ ] `overall_goals_difference` == `home_goals_difference` + `away_goals_difference`
- [ ] `overall_points` == 3 × `overall_matches_won` + 1 × `overall_matches_drawn`
- [ ] `home_points` == 3 × `home_matches_won` + 1 × `home_matches_drawn`
- [ ] `away_points` == 3 × `away_matches_won` + 1 × `away_matches_drawn`
- [ ] `overall_points` == `home_points` + `away_points`
- [ ] `len(overall_cumulative_points)` == `overall_matches`
- [ ] `len(home_cumulative_points)` == `home_matches`
- [ ] `len(away_cumulative_points)` == `away_matches`
- [ ] `overall_cumulative_points[-1]` == `overall_points` (if `overall_matches` > 0)
- [ ] `home_cumulative_points[-1]` == `home_points` (if `home_matches` > 0)
- [ ] `away_cumulative_points[-1]` == `away_points` (if `away_matches` > 0)
- [ ] `overall_cumulative_points` 연속 원소 차이 ∈ {0, 1, 3} (각 경기 결과에 해당)
- [ ] `home_cumulative_points` 연속 원소 차이 ∈ {0, 1, 3}
- [ ] `away_cumulative_points` 연속 원소 차이 ∈ {0, 1, 3}
- [ ] `overall_position` >= 1 (if not None)
- [ ] `home_position` >= 1 (if not None)
- [ ] `away_position` >= 1 (if not None)

**공격/수비/규율 통계 필드 정합성**

- [ ] `overall_stat_attack_passes_successful` <= `overall_stat_attack_passes`
- [ ] `overall_stat_attack_crosses_successful` <= `overall_stat_attack_crosses`
- [ ] `overall_stat_attack_long_balls_successful` <= `overall_stat_attack_long_balls`
- [ ] `overall_stat_defense_tackles_successful` <= `overall_stat_defense_tackles`
- [ ] `overall_stat_defense_duels_won` <= `overall_stat_defense_duels_total`
- [ ] `overall_stat_defense_duels_aerial_won` <= `overall_stat_defense_duels_aerial_total`
- [ ] `overall_stat_defense_duels_ground_won` <= `overall_stat_defense_duels_ground_total`
- [ ] `overall_stat_defense_duels_total` == `overall_stat_defense_duels_aerial_total` + `overall_stat_defense_duels_ground_total`
- [ ] `overall_stat_defense_duels_won` == `overall_stat_defense_duels_aerial_won` + `overall_stat_defense_duels_ground_won`
- [ ] `overall_stat_discipline_red_cards_direct` <= `overall_stat_discipline_red_cards`
- [ ] `overall_stat_average_possession`: 0.0 <= x <= 100.0
- [ ] `overall_stat_attack_shots_on_target` <= `overall_stat_attack_total_shots`
- [ ] 모든 integer stat 필드 >= 0
- [ ] `overall_stat_attack_expected_goals` >= 0.0
- [ ] `overall_stat_attack_expected_assists` >= 0.0

**교차 검증 (TeamStat ↔ Match/MatchStat)**

- [ ] `overall_goals_for` == Σ(해당 팀이 득점한 match별 골 수: 홈일 때 `home_team_score`, 어웨이일 때 `away_team_score`)
- [ ] `overall_goals_against` == Σ(해당 팀이 실점한 match별 골 수)
- [ ] `overall_matches` == `len(team_stat.match_associations)`
- [ ] `overall_stat_discipline_yellow_cards` == Σ(`MatchStat.discipline_yellow_cards` for 해당 팀 경기들)
- [ ] `overall_stat_discipline_red_cards` == Σ(`MatchStat.discipline_red_cards` for 해당 팀 경기들)
- [ ] `overall_stat_attack_corners` == Σ(`MatchStat.corners` for 해당 팀 경기들)
- [ ] `overall_stat_attack_total_shots` == Σ(`MatchStat.shots_total` for 해당 팀 경기들)
- [ ] `overall_stat_attack_shots_on_target` == Σ(`MatchStat.shots_on_target` for 해당 팀 경기들)
- [ ] `overall_stat_defense_clean_sheets` == count(해당 팀이 무실점한 경기 수)
- [ ] `overall_stat_defense_blocks` == Σ(`MatchStat.defense_blocks`)
- [ ] `overall_stat_defense_interceptions` == Σ(`MatchStat.defense_interceptions`)
- [ ] `overall_stat_defense_tackles` == Σ(`MatchStat.defense_tackles_total`)
- [ ] `overall_stat_defense_tackles_successful` == Σ(`MatchStat.defense_tackles_won`)

**교차 검증 (TeamStat ↔ PlayerStat)**

- [ ] `overall_goals_for` ≈ Σ(`PlayerStat.shooting_goals` for 해당 팀+시즌 소속 선수들) — own goal로 인해 약간의 차이 허용

**FK 존재 검증**

- [ ] `team_id` → teams 테이블에 존재
- [ ] `season_id` → seasons 테이블에 존재
- [ ] `ground_id` → grounds 테이블에 존재 (if not None)
- [ ] `manager_id` → staffs 테이블에 존재 (if not None)

#### 5-2. PlayerStat 검증

**자체 정합성 (단일 entity 내 필드 간 관계)**

- [ ] `appearances` >= 0
- [ ] `minutes_played` >= 0
- [ ] `number` >= 1
- [ ] `score_shooting`: 0.0 <= x <= 100.0
- [ ] `score_passing`: 0.0 <= x <= 100.0
- [ ] `score_defending`: 0.0 <= x <= 100.0
- [ ] `score_dribbling`: 0.0 <= x <= 100.0
- [ ] `score_discipline`: 0.0 <= x <= 100.0
- [ ] `score_overall`: 0.0 <= x <= 100.0

**슈팅 필드**

- [ ] `shooting_goals_penalty` <= `shooting_penalties_taken` (if both not None)
- [ ] `shooting_shots_on_target` <= `shooting_shots` (if both not None)
- [ ] `shooting_expected_goals` >= 0.0 (if not None)
- [ ] `shooting_expected_goals_non_penalty` <= `shooting_expected_goals` (if both not None)
- [ ] `shooting_expected_goals_non_penalty` ≈ `shooting_expected_goals` - 0.79 × `shooting_penalties_taken` (파생 필드 재계산)
- [ ] `shooting_goals` >= 0 (if not None)

**패스 필드**

- [ ] `passing_passes_successful` <= `passing_passes_total` (if both not None)
- [ ] `passing_crosses_successful` <= `passing_crosses_total` (if both not None)
- [ ] `passing_long_balls_accurate` <= `passing_long_balls_total` (if both not None)
- [ ] `passing_assists` >= 0 (if not None)
- [ ] `passing_chances_created` >= `passing_assists` (if both not None; chances_created = assists + key_passes)
- [ ] `passing_expected_assists` >= 0.0 (if not None)

**수비 필드**

- [ ] `defending_tackles_won` <= `defending_tackles_total` (if both not None)
- [ ] `defending_duels_won` <= `defending_duels_total` (if both not None)
- [ ] `defending_duels_aerial_won` <= `defending_duels_aerial_total` (if both not None)
- [ ] `defending_duels_ground_won` <= `defending_duels_ground_total` (if both not None)
- [ ] `defending_duels_total` == `defending_duels_aerial_total` + `defending_duels_ground_total` (if all not None)
- [ ] `defending_duels_won` == `defending_duels_aerial_won` + `defending_duels_ground_won` (if all not None)
- [ ] `defending_interceptions` >= 0 (if not None)
- [ ] `defending_recoveries` >= 0 (if not None)
- [ ] `defending_blocked` >= 0 (if not None)

**골키퍼 필드**

- [ ] `goalkeeping_penalty_saved` <= `goalkeeping_penalties_faced` (if both not None)
- [ ] `goalkeeping_penalty_goals_conceded` <= `goalkeeping_penalties_faced` (if both not None)
- [ ] `goalkeeping_penalty_saved` + `goalkeeping_penalty_goals_conceded` <= `goalkeeping_penalties_faced` (if all not None)
- [ ] `goalkeeping_saves` >= 0 (if not None)
- [ ] `goalkeeping_goals_prevented` ≈ xGoT_conceded - `goalkeeping_goals_conceded` (파생 필드 재계산)
- [ ] `goalkeeping_clean_sheets` <= `appearances` (if both not None)

**소유/드리블 필드**

- [ ] `possession_dribble_successful` <= `possession_dribble_total` (if both not None)
- [ ] `possession_touches` >= 0 (if not None)
- [ ] `possession_touches_in_opposition_box` <= `possession_touches` (if both not None)

**규율 필드**

- [ ] `discipline_yellow_cards` >= 0 (if not None)
- [ ] `discipline_red_cards` >= 0 (if not None)
- [ ] `discipline_red_cards_direct` <= `discipline_red_cards` (if both not None)
- [ ] `discipline_red_cards` <= `appearances` (if both not None; 경기당 최대 1장)

**교차 검증 (PlayerStat ↔ Match/Season)**

- [ ] `appearances` <= 해당 시즌 해당 팀의 총 경기 수
- [ ] 선수가 해당 시즌에 `PlayerChampionshipAssociation`으로 등록되어 있는지
- [ ] 선수가 해당 팀의 `TeamChampionshipAssociation`으로 등록된 시즌인지

**FK 존재 검증**

- [ ] `player_id` → players 테이블에 존재
- [ ] `team_id` → teams 테이블에 존재
- [ ] `season_id` → seasons 테이블에 존재

#### 5-3. Match 검증

**자체 정합성 (단일 entity 내 필드 간 관계)**

- [ ] `home_team_score` >= 0
- [ ] `away_team_score` >= 0
- [ ] `home_team_half_time_score` <= `home_team_score` (if not None)
- [ ] `away_team_half_time_score` <= `away_team_score` (if not None)
- [ ] `clock` >= 0
- [ ] `home_team_id` != `away_team_id`
- [ ] `attendance` >= 0 (if not None)
- [ ] `home_team_formation` 원소 합 == 10 (골키퍼 제외 outfield 선수 수)
- [ ] `away_team_formation` 원소 합 == 10
- [ ] `period` == FULLTIME인 경우에만 완전한 데이터 검증 수행

**교차 검증 (Match ↔ Lineup Association)**

- [ ] `lineup_associations`에서 `is_home=True`인 선수 수 == 11 (FULLTIME 경기)
- [ ] `lineup_associations`에서 `is_home=False`인 선수 수 == 11 (FULLTIME 경기)
- [ ] 라인업 선수의 `shirt_number`가 중복 없음 (같은 side 내)
- [ ] 라인업 선수의 `position`이 유효한 PositionEnum 값

**교차 검증 (Match ↔ Goal Association)**

- [ ] Σ(`goal_associations` where `is_home=True` and `is_own_goal=False`) + Σ(`goal_associations` where `is_home=False` and `is_own_goal=True`) == `home_team_score`
- [ ] Σ(`goal_associations` where `is_home=False` and `is_own_goal=False`) + Σ(`goal_associations` where `is_home=True` and `is_own_goal=True`) == `away_team_score`
- [ ] 골 scorer(`player_id`)가 해당 side의 lineup 또는 substitute에 포함
- [ ] 골 `clock` >= 0 and <= `match.clock`

**교차 검증 (Match ↔ Card Association)**

- [ ] 카드 받은 선수(`player_id`)가 해당 side의 lineup 또는 substitute에 포함
- [ ] 카드 `clock` >= 0 and <= `match.clock`
- [ ] `card_type`이 유효한 CardTypeEnum 값

**교차 검증 (Match ↔ Substitution Association)**

- [ ] 교체 횟수 <= 5 (현행 규정, side별)
- [ ] `in_player_id`가 `substitute_associations`(벤치)에 포함
- [ ] `out_player_id`가 `lineup_associations` 또는 이전 교체 `in_player`에 포함
- [ ] 교체 `clock` >= 0 and <= `match.clock`
- [ ] 교체 `clock`가 시간순으로 정렬되어 있는지

**교차 검증 (Match ↔ Fixture)**

- [ ] `Match.home_team_id` == `Fixture.home_team_id`
- [ ] `Match.away_team_id` == `Fixture.away_team_id`
- [ ] `fixture_id` → fixtures 테이블에 존재

**FK 존재 검증**

- [ ] `home_team_id` → teams 테이블에 존재
- [ ] `away_team_id` → teams 테이블에 존재
- [ ] `home_team_captain_id` → players 테이블에 존재 (if not None)
- [ ] `away_team_captain_id` → players 테이블에 존재 (if not None)
- [ ] `home_team_manager` → staffs 테이블에 존재 (if not None)
- [ ] `away_team_manager` → staffs 테이블에 존재 (if not None)
- [ ] `official_main_referee_id` → officials 테이블에 존재 (if not None)
- [ ] `official_assistant_1_referee_id` → officials 테이블에 존재 (if not None)
- [ ] `official_assistant_2_referee_id` → officials 테이블에 존재 (if not None)
- [ ] `official_fourth_referee_id` → officials 테이블에 존재 (if not None)
- [ ] `official_var_id` → officials 테이블에 존재 (if not None)
- [ ] `official_assistant_var_id` → officials 테이블에 존재 (if not None)

#### 5-4. MatchStat 검증

**자체 정합성 (단일 entity 내 필드 간 관계)**

- [ ] `shots_total` == `shots_inside_box` + `shots_outside_box`
- [ ] `shots_on_target` <= `shots_total`
- [ ] `shots_off_target` <= `shots_total`
- [ ] `shots_blocked` <= `shots_total`
- [ ] `duels_total` == `duels_aerial_total` + `duels_ground_total`
- [ ] `duels_won` == `duels_aerial_won` + `duels_ground_won`
- [ ] `duels_aerial_won` <= `duels_aerial_total`
- [ ] `duels_ground_won` <= `duels_ground_total`
- [ ] `duels_won` <= `duels_total`
- [ ] `duels_dribbles_successful` <= `duels_dribbles_total`
- [ ] `passes_accurate` <= `passes_total`
- [ ] `passes_accurate_crosses` <= `passes_total_crosses`
- [ ] `passes_accurate_long_balls` <= `passes_total_long_balls`
- [ ] `defense_tackles_won` <= `defense_tackles_total`
- [ ] `big_chances` >= `big_chances_missed` (big_chances = scored + missed)
- [ ] `possession`: 0.0 <= x <= 100.0
- [ ] `expected_goals` >= 0.0
- [ ] `expected_goals_non_penalty` <= `expected_goals`
- [ ] `expected_goals_on_target` >= 0.0
- [ ] `expected_goals_on_target` <= `expected_goals`
- [ ] 모든 Integer 필드 >= 0

**교차 검증 (MatchStat ↔ Match)**

- [ ] 각 Match에 정확히 2개의 MatchStat 존재 (home + away, FULLTIME 경기)
- [ ] MatchStat.`team_id` ∈ {Match.`home_team_id`, Match.`away_team_id`}
- [ ] 홈 MatchStat.`possession` + 어웨이 MatchStat.`possession` ≈ 100.0 (±1.0 오차 허용)

**FK 존재 검증**

- [ ] `match_id` → matches 테이블에 존재
- [ ] `team_id` → teams 테이블에 존재

#### 5-5. Fixture 검증

**자체 정합성 (단일 entity 내 필드 간 관계)**

- [ ] `home_team_id` != `away_team_id`
- [ ] `game_week` >= 1
- [ ] `kickoff_time`이 유효한 날짜/시간 값

**교차 검증 (Fixture ↔ Season)**

- [ ] `kickoff_time`이 시즌 기간(`date_start` ~ `date_end`) 범위 이내 (±1개월 허용)
- [ ] 시즌 내 동일 `home_team_id` + `away_team_id` + `game_week` 조합 중복 없음
- [ ] `home_team_id`가 해당 시즌에 `TeamChampionshipAssociation`으로 등록
- [ ] `away_team_id`가 해당 시즌에 `TeamChampionshipAssociation`으로 등록

**교차 검증 (Fixture ↔ Match)**

- [ ] FULLTIME 경기 기준, 각 Fixture에 정확히 1개의 Match 존재

**FK 존재 검증**

- [ ] `home_team_id` → teams 테이블에 존재
- [ ] `away_team_id` → teams 테이블에 존재
- [ ] `season_id` → seasons 테이블에 존재
- [ ] `ground_id` → grounds 테이블에 존재 (if not None)

#### 5-6. Season 검증

**자체 정합성 (단일 entity 내 필드 간 관계)**

- [ ] `date_start` < `date_end`
- [ ] `year_start` < `year_end` 또는 `year_start` == `year_end`
- [ ] `year_end` - `year_start` <= 1
- [ ] `abbreviation`이 비어 있지 않음

**교차 검증 (Season ↔ Fixture/Team)**

- [ ] 시즌에 최소 1개의 Fixture 존재
- [ ] 시즌에 등록된 팀(`TeamChampionshipAssociation`) 수가 합리적 범위 (예: 10~30)
- [ ] 시즌에 등록된 팀 수와 Fixture에 등장하는 고유 팀 수 일치

**FK 존재 검증**

- [ ] `competition_id` → competitions 테이블에 존재

#### 5-7. Competition 검증

**자체 정합성**

- [ ] `name_en` 비어 있지 않음
- [ ] `abbreviation` 비어 있지 않음
- [ ] `source_id` ∈ 허용 목록 ("1", "2", "5", "6", "8", "1007", "1125")

**교차 검증 (Competition ↔ Season)**

- [ ] 각 Competition에 최소 1개의 Season 존재

#### 5-8. Player 검증

**자체 정합성**

- [ ] `display_name_en` 비어 있지 않음
- [ ] `full_name` 비어 있지 않음
- [ ] `position`이 유효한 PositionEnum 값
- [ ] `preferred_foot`이 유효한 SideEnum 값
- [ ] `height` > 0 (if not None)
- [ ] `weight` > 0 (if not None)
- [ ] `birth_date` < 현재 날짜 (if not None)

**교차 검증 (Player ↔ Season/PlayerStat)**

- [ ] 최소 1개의 `PlayerChampionshipAssociation` 존재
- [ ] `PlayerChampionshipAssociation`에 등록된 시즌마다 대응하는 `PlayerStat` 존재 여부 (WARNING)

#### 5-9. Analytics 검증

**자체 정합성**

- [ ] `key`가 유효한 AnalyticsKeyEnum 값
- [ ] `value`가 유한한 수 (not NaN, not Inf)
- [ ] `delta`가 None이거나 유한한 수

**파생 필드 재계산 (Analytics ↔ Match/MatchStat)**

- [ ] `PER_MATCH_GOALS`: `value` ≈ Σ(match별 `home_team_score` + `away_team_score`) / 완료 경기 수
- [ ] `TOTAL_GOALS`: `value` == Σ(match별 `home_team_score` + `away_team_score`)
- [ ] `PER_MATCH_YELLOW_CARDS`: `value` ≈ Σ(`MatchStat.discipline_yellow_cards`) / 완료 경기 수
- [ ] `TOTAL_RED_CARDS`: `value` == Σ(`MatchStat.discipline_red_cards`)
- [ ] `PER_MATCH_XG`: `value` ≈ Σ(`MatchStat.expected_goals`) / 완료 경기 수
- [ ] `PER_MATCH_SUBSTITUTIONS`: `value` ≈ Σ(`Match.substitution_associations` 수) / 완료 경기 수
- [ ] `PER_MATCH_PASS_ACCURACY`: `value` ≈ avg(경기별 패스 정확도 %)
- [ ] `delta` 재계산: `delta` ≈ ((`current_value` - `prev_season_value`) / `prev_season_value`) × 100 (이전 시즌 존재 시)

**FK 존재 검증**

- [ ] `season_id` → seasons 테이블에 존재

#### 5-10. News 검증

**자체 정합성**

- [ ] `title_en` 비어 있지 않음
- [ ] `title_kr` 비어 있지 않음
- [ ] `content_en` 비어 있지 않음
- [ ] `content_kr` 비어 있지 않음
- [ ] `author_en` 비어 있지 않은 배열
- [ ] `author_kr` 비어 있지 않은 배열
- [ ] `len(author_en)` == `len(author_kr)` (번역 쌍 일치)
- [ ] `url` 비어 있지 않음
- [ ] `thumbnail_url` 비어 있지 않음
- [ ] `publish_date` <= 현재 날짜
- [ ] `type`이 유효한 NewsTypeEnum 값
- [ ] `source`가 유효한 SourceEnum 값

**교차 검증 (News ↔ Team)**

- [ ] `team_associations`의 모든 `team_id` → teams 테이블에 존재

#### 5-11. Award 검증

**자체 정합성**

- [ ] `type`이 유효한 AwardTypeEnum 값

**교차 검증 (Award ↔ PlayerStat/Staff)**

- [ ] `PlayerStatAwardAssociation`의 `player_stat_id` → player_stats 테이블에 존재
- [ ] `StaffAwardAssociation`의 `staff_id` → staffs 테이블에 존재
- [ ] 수상 `date`가 유효한 날짜 값

#### 5-12. 전체 데이터셋 교차 검증 (Cross-Dataset)

**시즌 단위 통계 일관성**

- [ ] 시즌 내 모든 TeamStat의 `overall_goals_for` 합 == 모든 TeamStat의 `overall_goals_against` 합 (리그 내 총 득실점 대칭)
- [ ] 시즌 내 모든 TeamStat의 `overall_matches_won` 합 == 모든 TeamStat의 `overall_matches_lost` 합 (승패 대칭)
- [ ] 시즌 내 `overall_matches_drawn` 합이 짝수 (무승부는 항상 2팀)
- [ ] 시즌 내 모든 TeamStat의 `overall_matches` 합 == 시즌 전체 경기 수 × 2 (각 경기에 2팀 참여)
- [ ] Fixture 수 == 팀 수 × (팀 수 - 1) (더블 라운드 로빈 기준, 홈/어웨이 각 1회)

**source_id 유일성**

- [ ] 각 entity 타입별 `source_id` 중복 없음

**고아 레코드 검증**

- [ ] FK가 참조하는 모든 parent 레코드가 실제 존재
- [ ] Match 없는 Fixture가 합리적 수준인지 (미완료 경기 등)
- [ ] TeamStat 없는 팀+시즌 조합이 없는지 (WARNING)

### Phase 6: Scheduler 구현 (1주) - **대기 중**

- [ ] APScheduler 설정
- [ ] Job 클래스 구현
- [ ] 전체 통합 테스트

---

## 🎯 주요 결정 사항 (확정)

| 항목               | 결정                    | 근거                 |
|------------------|-----------------------|--------------------|
| **Migration 도구** | Alembic               | SQLAlchemy 공식, 안정적 |
| **Scheduler**    | APScheduler           | Async 지원, 단순 환경 적합 |
| **Entity 패턴**    | source/source_id 유지   | 멀티소스 지원, 확장성       |
| **Merger 설계**    | Abstraction 없이 구체적 구현 | 각 Merger 고유 로직     |
| **데이터 소스**       | 현재 3개 유지              | 추가 계획 없음           |

---

## 📖 문서 읽기 순서 (권장)

### 처음 시작하는 경우

1. `1_master_plan.md` (필수, 20분) - 전체 계획 파악
2. `2_current_state_analysis.md` (선택, 30분) - 현재 구조 파악
3. `3_calculation_formulas_reference.md` (필수 참고) - 모든 계산식 보존
4. **`4_combined_migration_plan.md` (필수, 15분 + 2-3시간) - Phase 0 전 준비 작업**
5. `5_phase_0_preparation.md` (필수, 10분 + 2-3일) - Phase 0 시작
6. `7_phase_1_repository.md` (필수, 15분) - Phase 1 시작
7. `8_schema_diff_analysis.md` (필수, 10분) - Schema Diff 해결
8. `9_phase_2_puller.md` (필수, 15분) - Phase 2 시작
9. `11_phase_3_merger.md` (필수, 20분) - Phase 3 시작

### Phase 진행 중

1. 해당 Phase 섹션 (`1_master_plan.md`)
2. 실행 가이드 (각 Phase별 문서: `5_phase_0_preparation.md`, `7_phase_1_repository.md`, `8_schema_diff_analysis.md`, `9_phase_2_puller.md`, `11_phase_3_merger.md`)
3. `2_current_state_analysis.md` (필요 시 참고)

### 새 팀원 온보딩

1. `2_current_state_analysis.md` - 현재 구조 이해
2. `1_master_plan.md` - 리팩토링 계획 이해
3. 진행 중인 Phase 문서

---

## 🔗 관련 문서

- **프로젝트 README**: `/README.md`
- **기여 가이드**: `/docs/CONTRIBUTION.md`
- **기존 Entity 코드**: `/football_data_manager/common/repositories/`
- **기존 Puller 코드**: `/football_data_manager/puller/services/`

---

## ❓ FAQ

### Q: 문서가 너무 많은데 어디서 시작하나요?

**A**: 파일명 번호 순서대로 읽으세요. `1_master_plan.md`부터 시작하면 됩니다.

### Q: Phase 0는 꼭 해야 하나요?

**A**: 네, 필수입니다. Alembic과 테스트 없이 리팩토링하면 위험합니다.

### Q: 2_current_state_analysis.md는 언제 보나요?

**A**: 선택사항입니다. 기존 구조를 상세히 알고 싶을 때 보세요.

### Q: 각 Phase별 상세 가이드는 어디 있나요?

**A**: Phase 0(`5`), Phase 1(`7`), Schema Diff(`8`), Phase 2(`9`), Phase 3(`11`), Phase 4(`12`), Phase 5(`13`) 작성 완료. Phase 6은 필요 시 작성 예정.

### Q: 6_ai_agnostic_migration_plan.md는 뭔가요?

**A**: 이미 완료된 작업 (claudedocs → refactoring_docs 이동, 파일 번호 체계)의 설계 의도를 기록한 문서입니다. 실행할 것 없음.

### Q: Merger abstraction을 왜 제거했나요?

**A**: 각 Merger가 서로 다른 여러 Response 타입을 처리해야 해서, 강제된 abstraction이 오히려 복잡도를 증가시킵니다.

---

## 📝 문서 업데이트 이력

### 2026-03-17

- `13_phase_5_data_validator.md`: 신규 작성 (Data Validator 구현 실행 가이드, Step 1-8, 12개 Validator + Orchestrator + Container)
- `0_README.md`: Phase 5 문서(#13) 목록 추가, Phase 5 섹션에 상세 가이드 링크 추가, FAQ 갱신

### 2026-02-23

- `12_phase_4_data_syncer.md`: OOM 방지 전략 보강 (메모리 관리 전략 섹션 추가, SyncContext ID 기반 경량화, 배치 처리, 세션 스코핑, 메모리 모니터링)
- `12_phase_4_data_syncer.md`: 신규 작성 (Data Syncer 구현 실행 가이드, 종속성 DAG, 11개 SyncTask, DependencyResolver, SyncOrchestrator)
- `0_README.md`: Phase 4 문서(#12) 목록 추가, Phase 4 섹션에 상세 가이드 링크 추가, FAQ 갱신
- `0_README.md`: Phase 5 Data Validator 검증 규칙 대폭 확장 (12개 섹션, entity별 필드 단위 검증 + 교차 검증 + FK 검증)
- `0_README.md`: Phase 4 (Data Syncer), Phase 5 (Data Validator) 추가, 기존 Phase 4 (Scheduler) → Phase 6으로 이동
- `11_phase_3_merger.md`: 신규 작성 (Merger 구현 실행 가이드, Step 1-16, 11개 Merger + Scorer + Container)
- `0_README.md`: Phase 2 완료 반영, Phase 3 문서 추가, 진행 상황 업데이트
- `0_README.md`: Phase 3 핵심 구현 완료 상태 반영 (테스트/통합 검증 진행 중)
- `11_phase_3_merger.md`: Phase 3 단위 테스트 체크리스트 대거 갱신 (서비스/머저/스코어러 검증)
- `0_README.md`: Phase 3 검증 상태를 단위 테스트 완료 기준으로 갱신
- `11_phase_3_merger.md`: MatchMerger/NewsMerger/품질 기준 체크리스트 추가 갱신 (통합 테스트 제외)
- `11_phase_3_merger.md`: archive 필드 매핑 보존 체크 완료 (통합 테스트 항목만 미완료)
- `0_README.md`: Phase 3 상태를 `pytest 30 passed` + archive parity 검증 기준으로 갱신
- `12_phase_4_data_syncer.md`: SyncContainer/DependencyResolver/11개 SyncTask/SyncOrchestrator/app.py sync 구현 반영
- `12_phase_4_data_syncer.md`: Phase 4 체크리스트 대거 갱신 (통합 테스트/메모리 피크 실측 제외)
- `0_README.md`: Phase 4 상태를 `핵심 구현 완료, 통합 검증 대기`로 갱신
- `tests/syncer/*`: dependency/context/orchestrator 단위 테스트 추가
- `requirements/essential.txt`: `psutil` 추가

### 2026-02-02

- `9_phase_2_puller.md`: 신규 작성 (Puller 리팩토링 실행 가이드, Step 1-11)
- `8_schema_diff_analysis.md`: 신규 작성 → Entity 코드 수정 완료, DB 마이그레이션 대기 중
- `7_phase_1_repository.md`: 상태 완료 ✅ (Phase 1 전 단계 완료, Association 분리 포함)
- `teams.py`: 4개 optional 컬럼 추가, icon_url __init__ 수정
- `player_stats.py`: minutes_played NOT NULL + server_default="0" 변경
- `env.py`: metadata 테이블 include_name 필터, render_as_string SSL 수정
- `0_README.md`: Phase 1 완료 반영, Schema Diff/Phase 2 문서 추가, 진행 상황 업데이트

### 2026-02-01

- `4_combined_migration_plan.md`: 실행 완료 (모든 체크박스 체크, 시간 추적 기록)
- `5_phase_0_preparation.md`: 실행 완료 (Alembic 설정, entity 복원, 메서드 정리, 문서 업데이트)
- `0_README.md`: Pre-Phase 0 및 Phase 0 완료 상태 반영

### 2026-01-26

- `master_plan.md`: 모든 결정사항 확정
- `phase_0_preparation.md`: 신규 작성, 섹션 순서 재구성 (백업 우선)
- `calculation_formulas_reference.md`: 신규 작성 (Player Scores + Team Momentum + Analytics 통합)
- `combined_migration_plan.md`: 신규 작성 (Legacy + AI 중립화 통합 실행 계획, 한글 내용)
- `ai_agnostic_migration_plan.md`: 신규 작성 (AI 중립화 설계 문서, 한글 내용)
- `README.md`: 업데이트 (새 문서 설명 추가, 중복 제거)
- `master_plan_feedback.md`: 삭제 (내용 반영 완료)
- `score_calculation_reference.md`: 삭제 (calculation_formulas_reference.md로 통합)
- `docs/refactor/`: 삭제 (refactoring_docs/으로 통합)

---

**Last Updated**: 2026-03-17
**Maintained By**: @jormal
