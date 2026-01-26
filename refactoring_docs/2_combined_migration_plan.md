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
mkdir -p scripts
mkdir -p archive/legacy_scripts

# 2.2 활성 스크립트 이동 (현재 사용 중)
git mv app.py scripts/app_cli.py
git mv b.py scripts/ops_pulselive_and_analytics.py
git mv c.py scripts/backfill_player_stat_scores.py

# 2.3 낡은 스크립트를 아카이브로 완전 분리
git mv a.py archive/legacy_scripts/migrate_old_to_new_schema.py

# 2.4 scripts README 생성
cat > scripts/README.md << 'EOF'
# Scripts 디렉토리

**목적**: 현재 사용 중인 운영 스크립트 (활성 코드만)

---

## 활성 스크립트

### `app_cli.py`
**목적**: CLI 엔트리 포인트 (헬스 체크 및 테스트)  
**사용법**: `python scripts/app_cli.py health`  
**상태**: ✅ 활성  

### `ops_pulselive_and_analytics.py`
**목적**: 데이터 pulling 오케스트레이션 및 analytics 계산  
**포함 내용**:
- Competition, Season, Team, Player, Match 데이터 pulling
- Analytics 계산 (골, 패스 정확도, xG, 카드)
- **Team Momentum Index** 계산 (ΔPPM + ΔxG z-score)
- Championship 우승자 식별
- Award pulling

**사용법**: 파일 내 `runrun()` 함수 참조  
**상태**: ✅ 활성  
**의존성**: PulseLive API, The Athletic API  

### `backfill_player_stat_scores.py`
**목적**: Bayesian shrinkage를 사용한 선수 성능 점수 계산  
**포함 내용**:
- 6가지 점수 계산: shooting, passing, defending, dribbling, discipline, overall
- Bayesian prior 계산
- 포지션별 가중치 overall 점수

**사용법**: `python scripts/backfill_player_stat_scores.py`  
**상태**: ✅ 활성  
**참조**: `refactoring_docs/5_calculation_formulas_reference.md`  

---

## 아카이브된 스크립트

오래되고 더 이상 사용하지 않는 스크립트는 `archive/legacy_scripts/`로 이동되었습니다.

**참조**: `archive/legacy_scripts/README.md`
EOF

# 2.5 archive README 생성
cat > archive/legacy_scripts/README.md << 'EOF'
# Legacy Scripts Archive

**경고**: 이 디렉토리의 스크립트는 더 이상 작동하지 않습니다.

---

## `migrate_old_to_new_schema.py`

**원래 위치**: `a.py` (root)  
**이동 날짜**: 2026-01-26  
**목적**: 구 repository 스키마에서 신 스키마로 데이터 마이그레이션  

**상태**: ⚠️ 작동 불가
- `old_repositories` import가 더 이상 존재하지 않음
- 히스토리 참조 목적으로만 보존

**Git 히스토리로 복원**:
```bash
git show pre-migration/legacy-scripts-2026-01-26:a.py
```
EOF

# 2.6 legacy map 생성
mkdir -p docs/refactor
cat > docs/refactor/legacy_map.md << 'EOF'
# Legacy Map: 마이그레이션 전 → 마이그레이션 후

**날짜**: 2026-01-26  
**스냅샷**: `pre-migration/legacy-scripts-2026-01-26` 태그  

## 파일 재배치

| 이전 경로 | 새 경로 | 이유 | 상태 |
|----------|---------|------|--------|
| `a.py` | `archive/legacy_scripts/migrate_old_to_new_schema.py` | 일회성 마이그레이션, `old_repositories` import 깨짐 | 아카이브됨 (작동 불가) |
| `b.py` | `scripts/ops_pulselive_and_analytics.py` | 활성 오케스트레이션 스크립트 | 활성 |
| `c.py` | `scripts/backfill_player_stat_scores.py` | 활성 점수 계산 알고리즘 | 활성 |
| `app.py` | `scripts/app_cli.py` | CLI 엔트리 포인트 | 활성 |

## 디렉토리 구분

### `scripts/` - 운영 코드 (활성)
현재 사용 중이거나 앞으로 사용할 스크립트만 포함

### `archive/` - 백업 및 히스토리
- `archive/legacy_scripts/` - 작동하지 않는 낡은 스크립트
- 미래 구현에 영향 없음

## 보존된 구현

이동된 스크립트의 모든 비즈니스 로직이 보존되었습니다:

1. **Team Momentum 공식** (`b.py`에서):
   - 위치: `scripts/ops_pulselive_and_analytics.py`
   - 문서: `refactoring_docs/5_calculation_formulas_reference.md` (Section 2)
   - 함수: `update_momentum()`

2. **Player Stat Scores** (`c.py`에서):
   - 위치: `scripts/backfill_player_stat_scores.py`
   - 문서: `refactoring_docs/5_calculation_formulas_reference.md` (Section 1)
   - 함수: 모든 `calculate_*_score()` 함수

3. **Analytics 계산** (`b.py`에서):
   - 위치: `scripts/ops_pulselive_and_analytics.py`
   - 문서: `refactoring_docs/5_calculation_formulas_reference.md` (Section 3)
   - 함수: `upsert_analytics()`

## 롤백 방법

```bash
# 전체 롤백
git reset --hard pre-migration/legacy-scripts-2026-01-26

# 특정 파일 롤백
git show pre-migration/legacy-scripts-2026-01-26:c.py > c.py
```

## 향후 리팩토링 (Phase 0 이후)

- `backfill_player_stat_scores.py` 로직 추출 → `football_data_manager/scoring/`
- `ops_pulselive_and_analytics.py` 로직 추출 → 도메인 모듈
- `archive/legacy_scripts/` 내용 검토 후 필요시 완전 제거
EOF

git add scripts/ archive/legacy_scripts/ docs/refactor/
git commit -m "refactor: reorganize root scripts and archive legacy code

Active scripts moved to scripts/:
- app.py → scripts/app_cli.py
- b.py → scripts/ops_pulselive_and_analytics.py
- c.py → scripts/backfill_player_stat_scores.py

Legacy code archived:
- a.py → archive/legacy_scripts/migrate_old_to_new_schema.py (stale, non-functional)

Added documentation:
- scripts/README.md (active scripts only)
- archive/legacy_scripts/README.md (archive explanation)
- docs/refactor/legacy_map.md (migration tracking)

Reason: 
- Clean root directory for Phase 0 preparation
- Separate active code from archived backups
- Prevent legacy code from affecting future implementation

Tag: pre-migration/legacy-scripts-2026-01-26"
```

**검증**:
```bash
# 활성 스크립트 이동 확인
ls -la scripts/
# 출력: app_cli.py, ops_pulselive_and_analytics.py, backfill_player_stat_scores.py, README.md

# 아카이브 확인
ls -la archive/legacy_scripts/
# 출력: migrate_old_to_new_schema.py, README.md

# root가 깨끗한지 확인
ls *.py  # setup.py만 있어야 함 (있다면)

# 활성 스크립트 테스트
python scripts/app_cli.py health  # "I'm healthy!" 출력되어야 함
```

---

### **Step 3: 검증 및 테스트** (10분)

```bash
# 3.1 디렉토리 구조 확인
echo "=== 디렉토리 구조 확인 ==="
tree -L 2 -d refactoring_docs/
tree -L 2 -d scripts/
tree -L 1 -d archive/

# 3.2 Root 디렉토리 정리 확인
echo "=== Root 디렉토리 정리 확인 ==="
ls *.py  # setup.py만 있어야 함 (있다면)

# 3.3 Python import 테스트
echo "=== Python imports 테스트 ==="
python -c "from football_data_manager.common.repositories import Base; print('✅ Imports OK')"

# 3.4 테스트 실행
echo "=== 테스트 실행 ==="
pytest -v

# 3.5 활성 스크립트 테스트
echo "=== 활성 스크립트 테스트 ==="
python scripts/app_cli.py health

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
echo "✅ Legacy Script 재구성 완료! Phase 0 준비 완료."
echo ""
echo "요약:"
echo "  - Root 디렉토리 정리 (a.py, b.py, c.py, app.py → scripts/)"
echo "  - 레거시 스크립트 아카이브 완료"
echo "  - 모든 코드가 Git 히스토리에 보존됨"
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
├── CLAUDE.md                            # (현재 존재, 이후 변경 예정)
├── scripts/                             # ✨ 새로 생성 (활성 코드만)
│   ├── README.md
│   ├── app_cli.py                       # app.py에서 이동
│   ├── ops_pulselive_and_analytics.py   # b.py에서 이동
│   └── backfill_player_stat_scores.py   # c.py에서 이동
├── refactoring_docs/                    # ✨ 이미 존재 (번호 매겨진 문서들)
│   ├── 0_README.md
│   ├── 1_master_plan.md
│   ├── 2_combined_migration_plan.md     # 이 파일
│   ├── 3_phase_0_preparation.md
│   ├── 4_current_state_analysis.md
│   ├── 5_calculation_formulas_reference.md
│   └── 6_ai_agnostic_migration_plan.md
├── archive/                             # ✨ 새로 생성 (백업 전용)
│   └── legacy_scripts/                  # ✨ 새로 생성
│       ├── README.md
│       └── migrate_old_to_new_schema.py # a.py에서 이동 (작동 불가)
├── backups/                             # ✨ 새로 생성 (gitignored)
│   └── pre_migration_20260126.dump
├── football_data_manager/               # (기존 코드베이스)
├── tests/                               # (기존 테스트)
└── ...

External:
  ../football_data_manager_backup_20260126.bundle  # Git bundle 백업
```

**주요 변경사항:**
- Root에서 a.py, b.py, c.py, app.py 제거
- scripts/ 디렉토리에 명확한 이름으로 재배치
- a.py는 archive/legacy_scripts/로 이동 (작동하지 않음)

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

### 이슈: 스크립트가 실행되지 않음

```bash
# 권한 수정
chmod +x scripts/*.py
chmod +x scripts/legacy/*.py
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
- [ ] 스크립트 실행 가능 (`python scripts/app_cli.py health`)
- [ ] Git 히스토리 깨끗 (`git log --oneline -5`)
- [ ] 스냅샷 태그 존재 (`git tag -l "pre-migration/*"`)
- [ ] Bundle 백업 존재 (`ls -lh ../football_data_manager_backup_*.bundle`)
- [ ] Root 디렉토리 깨끗 (`setup.py` 외 `.py` 파일 없음)
- [ ] **`scripts/`에 활성 코드만 존재** (legacy 없음)
- [ ] **`archive/legacy_scripts/`에 a.py 백업 존재**
- [ ] **`scripts/README.md`에 이동 내역 문서화됨**

---

## 시간 추적

| 단계 | 예상 | 실제 | 비고 |
|------|-----------|--------|-------|
| Step 0: 사전 확인 | 5분 | | |
| Step 1: 스냅샷 | 10분 | | |
| Step 2: Scripts 재구성 | 20분 | | |
| Step 3: 검증 | 10분 | | |
| Step 4: Phase 0 계속 | 5분 | | |
| **총계** | **50분** | | |

---

**상태**: ✅ 실행 준비 완료  
**다음**: 단계별로 순차 실행, 각 주요 단계 후 커밋  
**완료 후**: Phase 0 진행 (Alembic, pytest, 백업 스크립트)
