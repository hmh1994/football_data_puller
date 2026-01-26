# Legacy Script 재구성 계획: Phase 0 준비

**목적**: Root 레벨 레거시 스크립트를 정리하여 Phase 0 시작 준비

**날짜**: 2026-01-26
**예상 소요 시간**: 45분
**상태**: 실행 준비 완료

---

## 개요

Root 디렉토리의 레거시 스크립트들(a.py, b.py, c.py, app.py)을 정리합니다:

- **활성 스크립트**: `scripts/`로 이동하고 명확한 이름으로 변경
- **폐기 스크립트**: `archive/legacy_scripts/`로 백업

**목표**: Phase 0(Alembic, pytest, 백업 스크립트)를 시작할 수 있는 깔끔한 저장소 구조

---

## 사전 요구사항

- [ ] 모든 현재 변경사항 커밋 완료
- [ ] 올바른 브랜치에서 작업 중 (`main` 또는 `feature/issue-001.04`)
- [ ] 데이터베이스 접근 가능 (선택적 백업용)
- [ ] 테스트 통과 (`pytest`)

---

## 실행 단계

### **Step 0: 마이그레이션 전 체크리스트** (5분)

```bash
# 1. 현재 브랜치 확인
git branch --show-current

# 2. 커밋되지 않은 변경사항 확인
git status

# 3. 커밋되지 않은 문서가 있다면 먼저 커밋
git add refactoring_docs/
git commit -m "docs: complete Phase 0 planning and formula documentation

- Completed calculation_formulas_reference.md
- Updated refactoring README
- Added legacy map planning"

# 4. 테스트 통과 확인
pytest -v

# 5. Python import 동작 확인
python -c "from football_data_manager.common.repositories import Base; print('✅ Imports OK')"
```

---

### **Step 1: 불변 스냅샷 생성** (10분)

```bash
# 1.1 스냅샷 태그 생성
git tag -a pre-migration/legacy-scripts-2026-01-26 -m "Snapshot before legacy script reorganization

Preserves state before:
- Legacy script reorganization (a.py, b.py, c.py, app.py)
- Root directory cleanup
- Phase 0 preparation

Rollback: git reset --hard pre-migration/legacy-scripts-2026-01-26"

# 1.2 안전 브랜치 생성 (절대 rebase 금지)
git checkout -b backup/pre-migration-2026-01-26
git push origin backup/pre-migration-2026-01-26
git push origin pre-migration/legacy-scripts-2026-01-26

# 1.3 작업 브랜치로 복귀
git checkout feature/issue-001.04

# 1.4 git bundle 생성 (외부 백업)
git bundle create ../football_data_manager_backup_$(date +%Y%m%d).bundle --all
ls -lh ../football_data_manager_backup_*.bundle

# 1.5 선택사항: 데이터베이스 백업
mkdir -p backups
pg_dump -h localhost -U your_user -d football_data -Fc > backups/pre_migration_$(date +%Y%m%d).dump

# 1.6 .gitignore에 백업 디렉토리 추가 (이미 있다면 생략)
echo "" >> .gitignore
echo "# Backups (never commit)" >> .gitignore
echo "backups/" >> .gitignore
git add .gitignore
git commit -m "chore: ignore backup files"
```

**검증**:

```bash
git tag -l "pre-migration/*"  # 출력: pre-migration/legacy-scripts-2026-01-26
git branch -a | grep backup   # 출력: backup/pre-migration-2026-01-26
ls -lh ../football_data_manager_backup_*.bundle  # 파일 존재 확인
```

---

### **Step 2: Legacy Scripts 재구성** (20분)

```bash
# 2.1 디렉토리 생성
mkdir -p archive/legacy_scripts

# 2.2 레거시 스크립트를 아카이브로 이동
# app.py는 root에 그대로 유지 (메인 엔트리 포인트)
git mv a.py archive/legacy_scripts/migrate_old_to_new_schema.py
git mv b.py archive/legacy_scripts/ops_pulselive_and_analytics.py
git mv c.py archive/legacy_scripts/backfill_player_stat_scores.py

# 2.3 프로젝트 README 업데이트
cat >> README.md << 'EOF'

## Usage

### CLI Commands

`app.py` serves as the main entry point for all operations:

#### Start Master Process
```bash
python app.py run
```
Starts the master process with cron scheduler for periodic data pulling.

#### Pull Specific Entity Data
```bash
python app.py pull-data {entity-name}
```
Executes Puller and Merger for specific entity.

**Available entities:**
- `competition` - Competition data
- `season` - Season data
- `team` - Team data
- `player` - Player data
- `match` - Match data

**Example:**
```bash
python app.py pull-data player
```

#### Health Check
```bash
python app.py health
```
Checks build status and system health.

EOF

# 2.4 archive README 생성

cat > archive/legacy_scripts/README.md << 'EOF'

# Legacy Scripts Archive

**경고**: 이 디렉토리의 스크립트는 개별 실행이 불가능합니다.

---

## 마이그레이션 내역

모든 스크립트의 로직이 `app.py`로 통합되었습니다.

### `migrate_old_to_new_schema.py`

**원래 위치**: `a.py` (root)
**이동 날짜**: 2026-01-26
**목적**: 구 repository 스키마에서 신 스키마로 데이터 마이그레이션

**상태**: ⚠️ 작동 불가

- `old_repositories` import가 더 이상 존재하지 않음
- 히스토리 참조 목적으로만 보존

### `ops_pulselive_and_analytics.py`

**원래 위치**: `b.py` (root)
**이동 날짜**: 2026-01-26
**목적**: 데이터 pulling 오케스트레이션 및 analytics 계산

**상태**: 📦 아카이브됨

- Puller 로직 → `app.py pull-data {entity}` 명령으로 통합
- Cron 스케줄링 → `app.py run` 명령으로 통합
- 참조: `refactoring_docs/5_calculation_formulas_reference.md` (Section 2, 3)

### `backfill_player_stat_scores.py`

**원래 위치**: `c.py` (root)
**이동 날짜**: 2026-01-26
**목적**: 선수 성능 점수 계산

**상태**: 📦 아카이브됨

- 로직이 analytics 계산에 통합될 예정
- 필요시 `app.py pull-data player` 실행 시 자동 계산
- 참조: `refactoring_docs/5_calculation_formulas_reference.md` (Section 1)

---

## Git 히스토리로 복원

```bash
# 원본 파일 보기
git show pre-migration/legacy-scripts-2026-01-26:a.py
git show pre-migration/legacy-scripts-2026-01-26:b.py
git show pre-migration/legacy-scripts-2026-01-26:c.py
```

# 2.6 legacy map 생성

mkdir -p docs/refactor
cat > docs/refactor/legacy_map.md << 'EOF'

# Legacy Map: 마이그레이션 전 → 마이그레이션 후

**날짜**: 2026-01-26
**스냅샷**: `pre-migration/legacy-scripts-2026-01-26` 태그

## 스크립트 통합 전략

`app.py`를 메인 엔트리 포인트로 유지하고, 레거시 스크립트들을 아카이브로 이동

## 파일 재배치

| 이전 경로 | 새 경로 | 통합 위치 | 상태 |
|----------|---------|---------|------|
| `app.py` | `app.py` (root, 이동 없음) | 메인 엔트리 포인트 | ✅ 활성 |
| `b.py` | `archive/legacy_scripts/ops_pulselive_and_analytics.py` | `app.py run` / `app.py pull-data {entity}` | 📦 통합됨 |
| `c.py` | `archive/legacy_scripts/backfill_player_stat_scores.py` | (자동 계산) | 📦 통합됨 |
| `a.py` | `archive/legacy_scripts/migrate_old_to_new_schema.py` | (없음) | ⚠️ 작동 불가 |

## CLI 명령어 매핑

| 기존 실행 방법                  | 새 실행 방법                                    | 기능                          |
|---------------------------|--------------------------------------------|-----------------------------|
| `python app.py health`    | `python app.py health`             | 빌드 상태 & 헬스 체크               |
| `python b.py` (백그라운드 실행)  | `python app.py run`                | Master process (cron 스케줄러)  |
| `python b.py` (개별 entity) | `python app.py pull-data {entity}` | 특정 entity 데이터 pulling       |
| `python c.py`             | (자동 실행)                                    | Player analytics 계산 시 자동 포함 |
| `python a.py`             | (사용 불가)                                    | 구 스키마 마이그레이션                |

**Entity 예시**:

- `python app.py pull-data competition`
- `python app.py pull-data season`
- `python app.py pull-data team`
- `python app.py pull-data player`
- `python app.py pull-data match`

## 디렉토리 구분

### Root - 메인 엔트리 포인트
- `app.py`: 모든 기능을 명령어로 제공하는 통합 CLI (root에 위치)

### `archive/legacy_scripts/` - 백업 및 히스토리
- 개별 스크립트 원본 보존 (실행 불가)
- 로직은 `app.py`로 통합됨

## 보존된 구현

모든 비즈니스 로직이 `app.py`로 통합되었습니다:

1. **Cron 스케줄링** (`b.py`에서):
    - 명령어: `python app.py run`
    - 기능: Master process 시작, 정기적 데이터 pulling 스케줄 관리
    - 원본: `archive/legacy_scripts/ops_pulselive_and_analytics.py`

2. **Entity별 데이터 Pulling** (`b.py`에서):
    - 명령어: `python app.py pull-data {entity}`
    - 기능: 특정 entity에 대한 Puller + Merger 실행
    - 문서: `refactoring_docs/5_calculation_formulas_reference.md` (Section 2, 3)
    - 원본: `archive/legacy_scripts/ops_pulselive_and_analytics.py`

3. **Player Stat Scores** (`c.py`에서):
    - 통합 방식: Player analytics 계산 시 자동 실행
    - 문서: `refactoring_docs/5_calculation_formulas_reference.md` (Section 1)
    - 원본: `archive/legacy_scripts/backfill_player_stat_scores.py`

## 롤백 방법

```bash
# 전체 롤백
git reset --hard pre-migration/legacy-scripts-2026-01-26

# 특정 파일 롤백
git show pre-migration/legacy-scripts-2026-01-26:c.py > c.py
```

## 향후 리팩토링 (Phase 0 이후)

- `app.py` 로직 추출 → 도메인 모듈로 이동
- CLI는 얇은 래퍼로만 유지
- `archive/legacy_scripts/` 내용 검토 후 필요시 완전 제거
  EOF

git add README.md archive/legacy_scripts/ docs/refactor/
git commit -m "refactor: consolidate legacy scripts and keep app.py as main entry point

Script consolidation:
- app.py → kept in root as main entry point
- b.py logic → app.py run / app.py pull-data {entity} commands
- c.py logic → integrated into analytics calculation

Legacy code archived:
- a.py → archive/legacy_scripts/migrate_old_to_new_schema.py (non-functional)
- b.py → archive/legacy_scripts/ops_pulselive_and_analytics.py (logic moved)
- c.py → archive/legacy_scripts/backfill_player_stat_scores.py (logic moved)

Added documentation:
- README.md usage section (CLI commands)
- archive/legacy_scripts/README.md (archive explanation)
- docs/refactor/legacy_map.md (migration tracking)

Benefits:
- app.py as obvious main entry point
- Shorter commands: python app.py {command}
- Clean root directory with only essential files

Tag: pre-migration/legacy-scripts-2026-01-26"

```

**검증**:
```bash
# Root에 app.py 확인
ls -la app.py

# 아카이브 확인
ls -la archive/legacy_scripts/
# 출력: migrate_old_to_new_schema.py, ops_pulselive_and_analytics.py, backfill_player_stat_scores.py, README.md

# root가 깨끗한지 확인
ls *.py  # setup.py만 있어야 함 (있다면)

# 통합 CLI 테스트
python app.py health  # "I'm healthy!" 출력되어야 함
```

---

### **Step 3: 검증 및 테스트** (10분)

```bash
# 3.1 디렉토리 구조 확인
echo "=== 디렉토리 구조 확인 ==="
tree -L 2 -d refactoring_docs/
tree -L 1 -d archive/

# 3.2 Root 디렉토리 정리 확인
echo "=== Root 디렉토리 정리 확인 ==="
ls *.py  # app.py (그리고 setup.py, 있다면) 만 있어야 함

# 3.3 Python import 테스트
echo "=== Python imports 테스트 ==="
python -c "from football_data_manager.common.repositories import Base; print('✅ Imports OK')"

# 3.4 테스트 실행
echo "=== 테스트 실행 ==="
pytest -v

# 3.5 통합 CLI 테스트
echo "=== 통합 CLI 테스트 ==="
python app.py health

# 3.6 git 상태 확인
echo "=== Git status ==="
git status

# 3.7 최근 커밋 확인
echo "=== 최근 커밋 ==="
git log --oneline -5

echo ""
echo "✅ 검증 완료!"
```

---

### **Step 4: Phase 0 작업 계속** (5분)

```bash
echo ""
echo "✅ Legacy Script 통합 완료! Phase 0 준비 완료."
echo ""
echo "요약:"
echo "  - Root 디렉토리 정리 완료"
echo "  - 모든 스크립트를 app.py로 통합"
echo "  - 개별 스크립트는 archive/legacy_scripts/에 보존"
echo "  - 모든 코드가 Git 히스토리에 보존됨"
echo ""
echo "통합된 CLI 명령어:"
echo "  - python app.py health                    # 빌드 상태 & 헬스 체크"
echo "  - python app.py run                       # Master process (cron 스케줄러)"
echo "  - python app.py pull-data {entity-name}   # 특정 entity 데이터 pulling"
echo ""
echo "Entity 예시:"
echo "  - python app.py pull-data competition"
echo "  - python app.py pull-data season"
echo "  - python app.py pull-data team"
echo "  - python app.py pull-data player"
echo "  - python app.py pull-data match"
echo ""
echo "백업 정보:"
echo "  - 전체 백업: ../football_data_manager_backup_$(date +%Y%m%d).bundle"
echo "  - 스냅샷 태그: pre-migration/legacy-scripts-2026-01-26"
echo "  - 안전 브랜치: backup/pre-migration-2026-01-26"
echo ""
echo "다음 단계 (refactoring_docs/3_phase_0_preparation.md 참조):"
echo "  1. requirements/essential.txt에 alembic>=1.13.0 추가"
echo "  2. requirements/test.txt에 pytest-cov, pytest-mock 추가"
echo "  3. pyproject.toml에 pytest 설정 업데이트"
echo "  4. tests/conftest.py에 fixtures 업데이트"
echo "  5. Alembic 초기화"
echo ""
```

---

## 최종 디렉토리 구조

```
football_data_puller/
├── app.py                               # ✨ 메인 엔트리 포인트 (root에 유지)
├── CLAUDE.md                            # (현재 존재, 이후 변경 예정)
├── README.md                            # ✨ CLI usage 섹션 추가
├── refactoring_docs/                    # ✨ 이미 존재 (번호 매겨진 문서들)
│   ├── 0_README.md
│   ├── 1_master_plan.md
│   ├── 2_combined_migration_plan.md     # 이 파일
│   ├── 3_phase_0_preparation.md
│   ├── 4_current_state_analysis.md
│   ├── 5_calculation_formulas_reference.md
│   └── 6_ai_agnostic_migration_plan.md
├── docs/
│   └── refactor/
│       └── legacy_map.md                # ✨ 새로 생성 (마이그레이션 추적)
├── archive/                             # ✨ 새로 생성 (백업 전용)
│   └── legacy_scripts/                  # ✨ 새로 생성
│       ├── README.md
│       ├── migrate_old_to_new_schema.py # a.py → 작동 불가
│       ├── ops_pulselive_and_analytics.py # b.py → app.py로 통합됨
│       └── backfill_player_stat_scores.py # c.py → app.py로 통합됨
├── backups/                             # ✨ 새로 생성 (gitignored)
│   └── pre_migration_20260126.dump
├── football_data_manager/               # (기존 코드베이스)
├── tests/                               # (기존 테스트)
└── ...

External:
  ../football_data_manager_backup_20260126.bundle  # Git bundle 백업
```

**주요 변경사항:**
- Root에서 a.py, b.py, c.py 제거
- app.py는 root에 유지 (메인 엔트리 포인트)
- 명령어 기반 실행 구조로 변경:
    - `app.py health` - 빌드 상태 & 헬스 체크
    - `app.py run` - Master process (cron 스케줄러)
    - `app.py pull-data {entity}` - 특정 entity 데이터 pulling
- 개별 스크립트는 archive/legacy_scripts/에 보존

---

## 롤백 절차

### 전체 롤백

```bash
# 마이그레이션 전 상태로 리셋
git reset --hard pre-migration/legacy-scripts-2026-01-26

# 또는 안전 브랜치로 checkout
git checkout backup/pre-migration-2026-01-26
```

### 부분 롤백 (특정 파일)

```bash
# 스냅샷에서 단일 파일 복원
git show pre-migration/legacy-scripts-2026-01-26:c.py > c.py
git add c.py
git commit -m "rollback: restore c.py from pre-migration snapshot"
```

### 긴급 복구 (Bundle에서)

```bash
# 로컬 repo가 손상된 경우
cd ..
git clone football_data_manager_backup_20260126.bundle recovered_repo
cd recovered_repo
```

---

## 문제 해결

### 이슈: 마이그레이션 후 테스트 실패

```bash
# import 확인
python -c "from football_data_manager.common.repositories import Base"

# pytest 설정 확인
pytest --collect-only

# 자세한 출력으로 실행
pytest -vv
```

### 이슈: CLI가 실행되지 않음

```bash
# 권한 수정
chmod +x app.py
```

### 이슈: 문서 참조 깨짐

```bash
# 수동으로 업데이트 후 커밋
git add -A
git commit -m "fix: update broken documentation links"
```

---

## 성공 기준

- [ ] 모든 테스트 통과 (`pytest -v`)
- [ ] 통합 CLI 실행 가능 (`python app.py health`)
- [ ] Git 히스토리 깨끗 (`git log --oneline -5`)
- [ ] 스냅샷 태그 존재 (`git tag -l "pre-migration/*"`)
- [ ] Bundle 백업 존재 (`ls -lh ../football_data_manager_backup_*.bundle`)
- [ ] **Root에 `app.py` 존재** (메인 엔트리 포인트)
- [ ] **Root에서 a.py, b.py, c.py 제거됨**
- [ ] **`archive/legacy_scripts/`에 a.py, b.py, c.py 백업 존재**
- [ ] **`README.md`에 CLI usage 섹션 추가됨**
- [ ] **`docs/refactor/legacy_map.md`에 마이그레이션 추적 문서 존재**

---

## 시간 추적

| 단계                  | 예상      | 실제 | 비고 |
|---------------------|---------|----|----|
| Step 0: 사전 확인       | 5분      |    |    |
| Step 1: 스냅샷         | 10분     |    |    |
| Step 2: Scripts 재구성 | 20분     |    |    |
| Step 3: 검증          | 10분     |    |    |
| Step 4: Phase 0 계속  | 5분      |    |    |
| **총계**              | **50분** |    |    |

---

**상태**: ✅ 실행 준비 완료
**다음**: 단계별로 순차 실행, 각 주요 단계 후 커밋
**완료 후**: Phase 0 진행 (Alembic, pytest, 백업 스크립트)
