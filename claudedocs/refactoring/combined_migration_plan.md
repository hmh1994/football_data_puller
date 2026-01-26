# 통합 마이그레이션 계획: Phase 0 준비

**목적**: Legacy Script 백업 + AI 중립화 마이그레이션 통합 실행 계획

**날짜**: 2026-01-26  
**예상 소요 시간**: 2-3시간  
**상태**: 실행 준비 완료  

---

## 개요

이 계획은 두 가지 마이그레이션을 통합합니다:
1. **Legacy Scripts 백업**: Root 레벨 스크립트를 `scripts/`로 이동
2. **AI 중립화 마이그레이션**: Claude 종속적인 디렉토리/파일 이름 변경

**목표**: Phase 0(Alembic, pytest, 백업 스크립트)를 시작할 수 있는 깔끔하고 도구 중립적인 저장소 구조

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
git add docs/ claudedocs/
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
# 1.1 포괄적 스냅샷 태그 생성
git tag -a pre-migration/combined-2026-01-26 -m "Snapshot before combined migration

Preserves state before:
- Legacy script reorganization (a.py, b.py, c.py, app.py)
- AI-agnostic directory renaming (claudedocs/, .claude/)
- Phase 0 preparation

Rollback: git reset --hard pre-migration/combined-2026-01-26"

# 1.2 안전 브랜치 생성 (절대 rebase 금지)
git checkout -b backup/pre-migration-2026-01-26
git push origin backup/pre-migration-2026-01-26
git push origin pre-migration/combined-2026-01-26

# 1.3 작업 브랜치로 복귀
git checkout main  # 또는 feature/issue-001.04

# 1.4 git bundle 생성 (외부 백업)
git bundle create ../football_data_manager_backup_$(date +%Y%m%d).bundle --all
ls -lh ../football_data_manager_backup_*.bundle

# 1.5 선택사항: 데이터베이스 백업
mkdir -p backups
pg_dump -h localhost -U your_user -d football_data -Fc > backups/pre_migration_$(date +%Y%m%d).dump

# 1.6 .gitignore에 백업 디렉토리 추가
echo "" >> .gitignore
echo "# Backups (never commit)" >> .gitignore
echo "backups/" >> .gitignore
git add .gitignore
git commit -m "chore: ignore backup files"
```

**검증**:
```bash
git tag -l "pre-migration/*"  # 출력: pre-migration/combined-2026-01-26
git branch -a | grep backup   # 출력: backup/pre-migration-2026-01-26
ls -lh ../football_data_manager_backup_*.bundle  # 파일 존재 확인
```

---

### **Step 2: Legacy Scripts 재구성** (20분)

```bash
# 2.1 디렉토리 생성
mkdir -p scripts/legacy
mkdir -p docs/refactor
mkdir -p archive/claude_desktop

# 2.2 활성 스크립트 이동
git mv app.py scripts/app_cli.py
git mv b.py scripts/ops_pulselive_and_analytics.py
git mv c.py scripts/backfill_player_stat_scores.py

# 2.3 오래된 스크립트를 legacy로 이동
git mv a.py scripts/legacy/migrate_old_to_new_schema.py

# 2.4 scripts README 생성
cat > scripts/README.md << 'EOF'
# Scripts 디렉토리

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
**참조**: `docs/ai_analysis/refactoring/calculation_formulas_reference.md`  

## Legacy Scripts

### `legacy/migrate_old_to_new_schema.py`
**목적**: 구 repository 스키마에서 신 스키마로 데이터 마이그레이션  
**상태**: ⚠️ 오래됨 (`old_repositories` import가 더 이상 존재하지 않음)  
**사용법**: 히스토리 참조용만  
EOF

# 2.5 legacy map 생성
cat > docs/refactor/legacy_map.md << 'EOF'
# Legacy Map: 마이그레이션 전 → 마이그레이션 후

**날짜**: 2026-01-26  
**스냅샷**: `pre-migration/combined-2026-01-26` 태그  

## 파일 재배치

| 이전 경로 | 새 경로 | 이유 | 상태 |
|----------|---------|------|--------|
| `a.py` | `scripts/legacy/migrate_old_to_new_schema.py` | 일회성 마이그레이션, `old_repositories` import 깨짐 | 오래됨 |
| `b.py` | `scripts/ops_pulselive_and_analytics.py` | 활성 오케스트레이션 스크립트 | 활성 |
| `c.py` | `scripts/backfill_player_stat_scores.py` | 활성 점수 계산 알고리즘 | 활성 |
| `app.py` | `scripts/app_cli.py` | CLI 엔트리 포인트 | 활성 |
| `CLAUDE.md` | `AI_GUIDELINES.md` | 도구 중립적 이름 | 활성 |
| `claudedocs/` | `docs/ai_analysis/` | 도구 중립적 이름 | 활성 |
| `claudescripts/` | `scripts/generated/` | 도구 중립적 이름 | 활성 |
| `.claude/` | `archive/claude_desktop/` | Claude Desktop 전용 설정 | 아카이브됨 |

## 보존된 구현

이동된 스크립트의 모든 비즈니스 로직이 보존되었습니다:

1. **Team Momentum 공식** (`b.py`에서):
   - 위치: `scripts/ops_pulselive_and_analytics.py`
   - 문서: `docs/ai_analysis/refactoring/calculation_formulas_reference.md` (Section 2)
   - 함수: `update_momentum()`

2. **Player Stat Scores** (`c.py`에서):
   - 위치: `scripts/backfill_player_stat_scores.py`
   - 문서: `docs/ai_analysis/refactoring/calculation_formulas_reference.md` (Section 1)
   - 함수: 모든 `calculate_*_score()` 함수

3. **Analytics 계산** (`b.py`에서):
   - 위치: `scripts/ops_pulselive_and_analytics.py`
   - 문서: `docs/ai_analysis/refactoring/calculation_formulas_reference.md` (Section 3)
   - 함수: `upsert_analytics()`

## 롤백 방법

```bash
# 전체 롤백
git reset --hard pre-migration/combined-2026-01-26

# 특정 파일 롤백
git show pre-migration/combined-2026-01-26:c.py > c.py
```

## 향후 리팩토링 (Phase 0 이후)

- `backfill_player_stat_scores.py` 로직 추출 → `football_data_manager/scoring/`
- `ops_pulselive_and_analytics.py` 로직 추출 → 도메인 모듈
- `scripts/legacy/` 완전히 폐기
EOF

git add scripts/ docs/refactor/
git commit -m "refactor: reorganize root scripts into scripts/ directory

Moved scripts:
- app.py → scripts/app_cli.py
- b.py → scripts/ops_pulselive_and_analytics.py
- c.py → scripts/backfill_player_stat_scores.py
- a.py → scripts/legacy/migrate_old_to_new_schema.py (stale)

Added documentation:
- scripts/README.md (usage guide)
- docs/refactor/legacy_map.md (migration tracking)

Reason: Clean root directory for Phase 0 preparation
Tag: pre-migration/combined-2026-01-26"
```

**검증**:
```bash
# 스크립트 이동 확인
ls -la scripts/
ls -la scripts/legacy/

# root가 깨끗한지 확인
ls *.py  # setup.py만 있어야 함 (있다면)

# 활성 스크립트 테스트
python scripts/app_cli.py health  # "I'm healthy!" 출력되어야 함
```

---

### **Step 3: AI 중립적 디렉토리 이름 변경** (15분)

```bash
# 3.1 문서 디렉토리 이름 변경
git mv claudedocs docs/ai_analysis
git mv claudescripts scripts/generated

# 3.2 .claude 디렉토리 아카이브
git mv .claude/* archive/claude_desktop/
rmdir .claude

git add -A
git commit -m "refactor: rename AI-specific directories to tool-agnostic names

Changes:
- claudedocs/ → docs/ai_analysis/
- claudescripts/ → scripts/generated/
- .claude/ → archive/claude_desktop/

Reason: Remove Claude-specific naming for multi-tool support
Part of: AI-agnostic migration (see docs/refactor/ai_agnostic_migration_plan.md)"
```

**검증**:
```bash
# 디렉토리 이름 변경 확인
ls -la docs/ai_analysis/
ls -la scripts/generated/
ls -la archive/claude_desktop/

# 이전 디렉토리가 없는지 확인
ls -la | grep -E "claude"  # archive/claude_desktop만 나와야 함
```

---

### **Step 4: 파일 이름 변경 및 내용 업데이트** (20분)

```bash
# 4.1 CLAUDE.md를 AI_GUIDELINES.md로 이름 변경
git mv CLAUDE.md AI_GUIDELINES.md

# 4.2 AI_GUIDELINES.md 내용 업데이트
cat > AI_GUIDELINES.md << 'EOF'
# AI 가이드라인

**목적**: AI 보조 개발을 위한 코딩 규칙 및 스타일 선호도

**적용 대상**: 모든 AI 코딩 어시스턴트 (Claude, Copilot, Cursor, OpenCode 등)

---

## 코드 스타일 선호도

### Python `__init__.py` 파일

**규칙**: `__init__.py` 파일을 비워두기

**근거**:
- 명시적 import가 가독성 향상
- 순환 import 이슈 방지
- 명확한 모듈 경계

**예시**:
```python
# ❌ 피하기
# football_data_manager/common/__init__.py
from .repositories import Base
from .services import DbService

# ✅ 권장
# football_data_manager/common/__init__.py
# (빈 파일)
```

---

## 프로젝트별 규칙

### Entity 패턴
- 모든 entity는 `source`와 `source_id` 필드를 가져야 함
- `BaseEntity`를 기본 클래스로 사용
- 참조: `docs/architecture/entity_design.md`

### Repository 패턴
- Async 전용 repository (sync 메서드 없음)
- `AsyncBaseRepository` 패턴 사용
- 참조: `docs/architecture/repository_design.md`

### 테스팅
- async 지원 pytest (`pytest-asyncio`)
- `tests/conftest.py`의 fixtures 사용
- 커버리지 목표: 80%+

---

## 문서화 표준

### Docstrings
- Google 스타일 docstrings 사용
- 시그니처에 타입 힌트 포함 (docstring이 아닌)
- 복잡한 알고리즘은 예제와 함께 문서화

### 주석
- "무엇"이 아닌 "왜"를 설명
- 복잡한 비즈니스 로직은 인라인 설명 필요
- 해당되는 경우 이슈 번호 참조

---

## AI 생성 코드

모든 AI 생성 코드는 반드시:
1. 병합 전 사람이 검토
2. 엣지 케이스를 커버하는 테스트 포함
3. 명확한 예제와 함께 문서화
4. 커밋 메시지에 AI 도구 참조

**커밋 형식**:
```
type(scope): description

AI-assisted: <tool name>
Reviewed-by: @username
```

---

**최종 업데이트**: 2026-01-26  
**유지 관리자**: Development Team
EOF

git add AI_GUIDELINES.md
git commit -m "docs: rename CLAUDE.md to AI_GUIDELINES.md with expanded content

- Generalized for all AI coding assistants
- Added comprehensive coding conventions
- Included project-specific patterns
- Added AI-generated code guidelines"
```

**검증**:
```bash
# 파일 이름 변경 및 존재 확인
cat AI_GUIDELINES.md | head -20
```

---

### **Step 5: 문서 메타데이터 업데이트** (15분)

**⚠️ 수동 단계 필요**:

다음 파일들의 상단에 YAML front matter 추가:
- `docs/ai_analysis/refactoring/master_plan.md`
- `docs/ai_analysis/refactoring/phase_0_preparation.md`
- `docs/ai_analysis/refactoring/current_state_analysis.md`
- `docs/ai_analysis/refactoring/calculation_formulas_reference.md`

**메타데이터 템플릿**:
```yaml
---
ai_generated: true
generated_date: 2026-01-26
ai_tool: Claude Sonnet 4
reviewed_by: @jormal
review_date: 2026-01-26
status: approved
last_updated: 2026-01-26
---
```

**수동 편집 후**:
```bash
git add docs/ai_analysis/
git commit -m "docs: add AI-generation metadata to documentation

- Added YAML front matter to all AI-generated docs
- Marked generation date, tool, reviewer
- Updated README with AI-generation disclaimer"
```

---

### **Step 6: 설정 파일 생성** (10분)

```bash
# 6.1 .aiignore 생성
cat > .aiignore << 'EOF'
# AI-Agnostic Ignore File
# AI 코딩 어시스턴트가 컨텍스트에서 제외할 파일

# Dependencies
node_modules/
venv/
*.egg-info/

# Build artifacts
dist/
build/
*.pyc
__pycache__/

# Secrets
.env
*.pem
*.key
configs/*.local.*

# Large data files
*.sql
*.dump
backups/

# Generated documentation (AI용 읽기 전용)
docs/api_reference/

# Test artifacts
.pytest_cache/
htmlcov/
.coverage

# IDE settings (도구별)
.vscode/
.idea/
.ai/
EOF

# 6.2 AI 도구용 .gitignore 업데이트
cat >> .gitignore << 'EOF'

# AI Assistant Settings (개인 설정)
.ai/*.local.*
.cursor/
.copilot/

# AI-generated temporary files
scripts/generated/*.tmp
docs/ai_analysis/*.draft.md
EOF

git add .aiignore .gitignore
git commit -m "chore: add AI-agnostic configuration files

- Created .aiignore for AI context filtering
- Updated .gitignore for multi-tool support
- Excludes secrets, large files, and build artifacts from AI context"
```

**검증**:
```bash
cat .aiignore | head -20
tail -10 .gitignore
```

---

### **Step 7: 내부 참조 업데이트** (15분)

**⚠️ 수동 단계 필요**:

이전 경로를 참조하는 모든 파일 찾기:
```bash
grep -r "claudedocs" . --exclude-dir=.git --exclude-dir=archive --exclude-dir=backups | cut -d: -f1 | sort -u
```

**업데이트할 패턴**:
- `claudedocs/refactoring/` → `docs/ai_analysis/refactoring/`
- `claudescripts/` → `scripts/generated/`
- `CLAUDE.md` → `AI_GUIDELINES.md`

**업데이트가 필요할 수 있는 파일**:
- `README.md`
- `docs/refactor/legacy_map.md`
- 내부 문서

**수동 편집 후**:
```bash
git add -A
git commit -m "docs: update references to renamed directories

- Updated all references from claudedocs/ to docs/ai_analysis/
- Updated CLAUDE.md references to AI_GUIDELINES.md
- Updated internal documentation links
- Ensured no broken references remain"
```

---

### **Step 8: 검증 및 테스트** (15분)

```bash
# 8.1 남아있는 'claude' 참조 확인
echo "=== 남아있는 'claude' 참조 확인 ==="
grep -r "claudedocs\|claudescripts\|CLAUDE.md" . \
  --exclude-dir=.git \
  --exclude-dir=archive \
  --exclude-dir=backups \
  --exclude="*.bundle"

# 비어있거나 archive/ 참조만 나와야 함

# 8.2 디렉토리 구조 확인
echo "=== 디렉토리 구조 확인 ==="
tree -L 2 -d docs/
tree -L 2 -d scripts/
tree -L 1 -d archive/

# 8.3 Python import 테스트
echo "=== Python imports 테스트 ==="
python -c "from football_data_manager.common.repositories import Base; print('✅ Imports OK')"

# 8.4 테스트 실행
echo "=== 테스트 실행 ==="
pytest -v

# 8.5 활성 스크립트 테스트
echo "=== 활성 스크립트 테스트 ==="
python scripts/app_cli.py health

# 8.6 git 상태 확인
echo "=== Git status ==="
git status

# 8.7 최근 커밋 확인
echo "=== 최근 커밋 ==="
git log --oneline -10

echo ""
echo "✅ 검증 완료!"
```

---

### **Step 9: Phase 0 작업 브랜치 생성** (5분)

```bash
# 9.1 Phase 0 브랜치 생성
git checkout -b refactor/phase-0

# 9.2 브랜치 확인
git branch --show-current

echo ""
echo "✅ 마이그레이션 완료! Phase 0 준비 완료."
echo ""
echo "요약:"
echo "  - Root 디렉토리 정리 (scripts가 scripts/로 이동)"
echo "  - AI 중립적 이름 (docs/ai_analysis/, scripts/generated/)"
echo "  - 모든 코드가 Git 히스토리에 보존됨"
echo "  - 전체 백업: ../football_data_manager_backup_$(date +%Y%m%d).bundle"
echo "  - 스냅샷 태그: pre-migration/combined-2026-01-26"
echo "  - 안전 브랜치: backup/pre-migration-2026-01-26"
echo ""
echo "다음 단계:"
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
├── AI_GUIDELINES.md                     # ✨ CLAUDE.md에서 이름 변경
├── .aiignore                            # ✨ 새로 생성
├── scripts/                             # ✨ 새로 생성
│   ├── README.md
│   ├── app_cli.py                       # app.py에서 이동
│   ├── ops_pulselive_and_analytics.py   # b.py에서 이동
│   ├── backfill_player_stat_scores.py   # c.py에서 이동
│   ├── legacy/
│   │   └── migrate_old_to_new_schema.py # a.py에서 이동
│   └── generated/                       # ✨ claudescripts/에서 이름 변경
│       └── README.md
├── docs/
│   ├── ai_analysis/                     # ✨ claudedocs/에서 이름 변경
│   │   ├── refactoring/
│   │   │   ├── README.md               # 메타데이터로 업데이트됨
│   │   │   ├── master_plan.md          # YAML front matter 추가
│   │   │   ├── calculation_formulas_reference.md
│   │   │   ├── current_state_analysis.md
│   │   │   └── phase_0_preparation.md
│   │   ├── entity-update-analysis.md
│   │   └── player-stat-score.md
│   └── refactor/
│       ├── legacy_map.md                # ✨ 새로 생성
│       └── ai_agnostic_migration_plan.md
├── archive/
│   └── claude_desktop/                  # ✨ .claude/에서 이동
│       ├── settings.local.json
│       └── update_championship.md
├── backups/                             # ✨ 새로 생성 (gitignored)
│   └── pre_migration_20260126.dump
└── ...

External:
  ../football_data_manager_backup_20260126.bundle  # Git bundle 백업
```

---

## 롤백 절차

### 전체 롤백

```bash
# 마이그레이션 전 상태로 리셋
git reset --hard pre-migration/combined-2026-01-26

# 또는 안전 브랜치로 checkout
git checkout backup/pre-migration-2026-01-26
```

### 부분 롤백 (특정 파일)

```bash
# 스냅샷에서 단일 파일 복원
git show pre-migration/combined-2026-01-26:c.py > c.py
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

### 이슈: 문서의 내부 링크 깨짐

```bash
# 깨진 참조 찾기
grep -r "claudedocs\|CLAUDE.md" docs/ --exclude-dir=.git

# 수동으로 업데이트 후 커밋
git add -A
git commit -m "fix: update broken documentation links"
```

---

## 성공 기준

- [ ] 모든 테스트 통과 (`pytest -v`)
- [ ] 활성 코드에 `claudedocs` 참조 없음 (`grep -r "claudedocs" . --exclude-dir=archive`)
- [ ] 스크립트 실행 가능 (`python scripts/app_cli.py health`)
- [ ] Git 히스토리 깨끗 (`git log --oneline -10`)
- [ ] 스냅샷 태그 존재 (`git tag -l "pre-migration/*"`)
- [ ] Bundle 백업 존재 (`ls -lh ../football_data_manager_backup_*.bundle`)
- [ ] Root 디렉토리 깨끗 (`setup.py` 외 `.py` 파일 없음)
- [ ] AI_GUIDELINES.md 존재 및 포괄적
- [ ] `.aiignore`가 민감한 파일 제외

---

## 시간 추적

| 단계 | 예상 | 실제 | 비고 |
|------|-----------|--------|-------|
| Step 0: 사전 확인 | 5분 | | |
| Step 1: 스냅샷 | 10분 | | |
| Step 2: Scripts 재구성 | 20분 | | |
| Step 3: 디렉토리 이름 변경 | 15분 | | |
| Step 4: 파일 이름 변경 | 20분 | | |
| Step 5: 메타데이터 | 15분 | | |
| Step 6: 설정 파일 | 10분 | | |
| Step 7: 참조 업데이트 | 15분 | | |
| Step 8: 검증 | 15분 | | |
| Step 9: Phase 0 브랜치 | 5분 | | |
| **총계** | **130분 (2시간 10분)** | | |

---

**상태**: ✅ 실행 준비 완료  
**다음**: 단계별로 순차 실행, 각 주요 단계 후 커밋  
**완료 후**: Phase 0 진행 (Alembic, pytest, 백업 스크립트)
