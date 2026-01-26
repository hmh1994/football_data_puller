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

- 4개 컴포넌트 구조 (Repository, Puller, Merger, Scheduler)
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

- [ ] **app.py 통합 CLI 구현 완료** (Step 2.3)
- [ ] Legacy scripts → `archive/legacy_scripts/` 이동 완료
- [ ] Root 디렉토리 정리 완료 (a.py, b.py, c.py 제거)
- [ ] Git 스냅샷 생성 완료

---

## 🚀 빠른 시작 (Phase 0)

### Step 1: 전체 계획 파악

```bash
# Master Plan 읽기 (20분)
cat refactoring_docs/1_master_plan.md
```

**핵심 확인사항**:

- [ ] 4개 컴포넌트 이해 (Repository, Puller, Merger, Scheduler)
- [ ] 목표 디렉토리 구조 확인
- [ ] Phase별 일정 확인 (총 6-8주 예상)

### Step 2: Phase 0 준비 시작

```bash
# Phase 0 가이드 읽기 (10분)
cat refactoring_docs/5_phase_0_preparation.md

# Alembic 설정 시작
alembic init football_data_manager/repository/migrations
```

**Phase 0 완료 기준**:

- [ ] Alembic 설치 완료
- [ ] alembic.ini 설정 완료
- [ ] env.py에서 ConfigService 통합 완료
- [ ] Alembic이 DB 설정을 읽을 수 있는지 검증 완료

### Step 3: (필요 시) 상세 구조 참고

```bash
# 현재 구조 상세 분석 보기
cat refactoring_docs/2_current_state_analysis.md
```

---

## 📋 Phase 진행 상황

### Phase 0: Preparation (1주) - **진행 예정**

- [ ] Alembic 설정
- [ ] pytest 테스트 프레임워크
- [ ] 데이터베이스 백업 전략

### Phase 1: Repository 리팩토링 (1-2주) - **대기 중**

- [ ] 디렉토리 구조 생성
- [ ] Entity 마이그레이션
- [ ] AsyncBaseRepository 구현

### Phase 2: Puller 리팩토링 (1-2주) - **대기 중**

- [ ] Interface 구조 생성
- [ ] AbstractPuller 구현
- [ ] 기존 Puller 마이그레이션

### Phase 3: Merger 구현 (1-2주) - **대기 중**

- [ ] Merger 구조 생성
- [ ] 필요한 Merger 구현
- [ ] 통합 테스트

### Phase 4: Scheduler 구현 (1주) - **대기 중**

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

### Phase 진행 중

1. 해당 Phase 섹션 (`1_master_plan.md`)
2. 실행 가이드 (각 Phase별 문서, Phase 0만 현재 존재)
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

**A**: Phase 0만 현재 작성됨. Phase 1-4는 필요 시 작성 예정.

### Q: 6_ai_agnostic_migration_plan.md는 뭔가요?

**A**: 이미 완료된 작업 (claudedocs → refactoring_docs 이동, 파일 번호 체계)의 설계 의도를 기록한 문서입니다. 실행할 것 없음.

### Q: Merger abstraction을 왜 제거했나요?

**A**: 각 Merger가 서로 다른 여러 Response 타입을 처리해야 해서, 강제된 abstraction이 오히려 복잡도를 증가시킵니다.

---

## 📝 문서 업데이트 이력

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

**Last Updated**: 2026-01-26
**Maintained By**: @jormal
