# AI 중립화 마이그레이션 계획

**목적**: Claude 종속적인 의존성을 제거하고, 모든 AI 코딩 어시스턴트에서 사용 가능한 구조로 전환

**날짜**: 2026-01-26  
**상태**: ✅ 완료 (Integrated into `2_combined_migration_plan.md`)

---

## ⚠️ 이 문서는 설계 문서입니다

**실행 가이드**: `2_combined_migration_plan.md`를 참고하세요.

이 문서는 AI 중립화 마이그레이션의 **WHY**와 **WHAT**을 설명합니다.  
실제 **HOW** (실행 명령어)는 `2_combined_migration_plan.md`에 통합되었습니다.

---

## 현재 상태 (2026-01-26)

### ✅ 완료된 작업

| 항목 | 이전 | 현재 | 상태 |
|------|------|------|------|
| 문서 디렉토리 | `claudedocs/` | `refactoring_docs/` | ✅ 완료 |
| 문서 파일명 | 이름 없음 | 번호 접두사 (0-6) | ✅ 완료 |
| 레거시 스크립트 | `a.py, b.py, c.py` | `archive/legacy_scripts/` | ✅ 완료 |
| 메인 엔트리 포인트 | `app.py` (기존) | `app.py` (통합 CLI 구현) | ✅ 완료 |
| 스타일 가이드 | `CLAUDE.md` | (유지) | ✅ 완료 |

### 📁 최종 디렉토리 구조

```
football_data_puller/
├── app.py                               # 통합 CLI (메인 엔트리 포인트)
├── CLAUDE.md                            # 코드 스타일 가이드 (유지)
├── refactoring_docs/                    # AI 중립적 문서 (이전 claudedocs/)
│   ├── 0_README.md                      # 네비게이션 가이드
│   ├── 1_master_plan.md                 # 전체 계획
│   ├── 2_combined_migration_plan.md     # 실행 가이드 (Legacy + AI 중립화)
│   ├── 3_phase_0_preparation.md         # Phase 0 가이드
│   ├── 4_current_state_analysis.md      # 상세 분석
│   ├── 5_calculation_formulas_reference.md  # 계산식 참조
│   └── 6_ai_agnostic_migration_plan.md  # 이 문서 (설계)
├── archive/legacy_scripts/              # 레거시 백업
│   ├── migrate_old_to_new_schema.py     # a.py (작동 불가)
│   ├── ops_pulselive_and_analytics.py   # b.py (로직 → app.py)
│   └── backfill_player_stat_scores.py   # c.py (로직 → app.py)
├── docs/refactor/
│   └── legacy_map.md                    # 마이그레이션 추적
└── football_data_manager/               # 메인 코드베이스
```

---

## 마이그레이션 전략 (설계)

### 원칙

1. **도구 중립성**: 특정 AI 도구에 종속되지 않음
2. **명확한 구조**: 번호 매긴 파일로 읽기 순서 명확화
3. **실행 가능성**: 모든 단계가 복사-붙여넣기 가능한 명령어
4. **롤백 가능성**: Git 기반 스냅샷으로 안전한 롤백

### 주요 결정 사항

#### 1. 문서 디렉토리 이름

**선택**: `refactoring_docs/`

**이유**:
- ✅ 목적 명확 ("리팩토링 문서")
- ✅ AI 도구 중립적
- ✅ 다른 프로젝트에서도 일반적으로 사용
- ❌ `docs/ai_analysis/` - 너무 구체적, 중첩 깊음
- ❌ `docs/refactor/` - 이미 `docs/refactor/legacy_map.md` 존재

#### 2. 파일 이름 규칙

**선택**: 번호 접두사 (`0_README.md`, `1_master_plan.md`, ...)

**이유**:
- ✅ 읽기 순서 명확
- ✅ 파일 탐색기에서 자동 정렬
- ✅ 신규 팀원 온보딩 용이
- ❌ 알파벳순 - 읽기 순서 불명확

#### 3. Legacy Scripts 처리

**선택**: `archive/legacy_scripts/` + 통합 CLI (`app.py`)

**이유**:
- ✅ 개별 스크립트 → 단일 진입점 (명령어 기반)
- ✅ 코드 히스토리 보존 (Git)
- ✅ 향후 구현 경로 명확 (TODO 마커)
- ❌ `scripts/` 유지 - 여러 파일 관리 복잡

#### 4. CLAUDE.md 유지

**선택**: `CLAUDE.md` 그대로 유지

**이유**:
- ✅ 실제 코드에 영향 없음 (문서만)
- ✅ 프로젝트별 스타일 가이드로 유용
- ✅ 변경 시 Git 히스토리 추적 어려움
- ❌ `AI_GUIDELINES.md`로 변경 - 불필요한 복잡도

---

## 실행 가이드

### Step-by-Step 실행

**문서**: `2_combined_migration_plan.md`

```bash
# 1. 문서 읽기
cat refactoring_docs/2_combined_migration_plan.md

# 2. Step 0: 사전 확인
# 3. Step 1: Git 스냅샷 생성
# 4. Step 2: Legacy Scripts 재구성 + app.py 구현
# 5. Step 3: 검증
# 6. Step 4: Phase 0 진행
```

**예상 소요 시간**: 45분

**완료 기준**:
- ✅ app.py 통합 CLI 구현 완료
- ✅ a.py, b.py, c.py → archive/legacy_scripts/
- ✅ Git 스냅샷 생성 완료

---

## Why This Approach?

### Combined Migration

**이전 계획**: 
- AI 중립화 마이그레이션 (별도 단계)
- Legacy Script 정리 (별도 단계)

**변경**:
- **통합 실행** (`2_combined_migration_plan.md`)

**이유**:
1. ✅ 두 작업이 모두 "Phase 0 준비" 단계
2. ✅ 실행 시점이 동일 (리팩토링 시작 전)
3. ✅ 중복 단계 제거 (Git 스냅샷 등)
4. ✅ 사용자 경험 단순화

### App.py Integration

**핵심 변경**: 개별 스크립트 → 통합 CLI

**Before**:
```
python a.py  # 마이그레이션
python b.py  # 데이터 pulling
python c.py  # 점수 계산
```

**After**:
```
python app.py health                  # 헬스 체크
python app.py run                     # Master process
python app.py pull-data {entity}      # Entity 데이터 pulling
```

**장점**:
- ✅ 단일 진입점 (명확성)
- ✅ 확장 가능 (새 명령어 추가 쉬움)
- ✅ 표준 패턴 (Django manage.py, Flask app.py)

---

## 롤백 전략

### Git 기반 롤백

**스냅샷**:
```bash
git tag pre-migration/legacy-scripts-2026-01-26
git branch backup/pre-migration-2026-01-26
git bundle create ../football_data_manager_backup_20260126.bundle --all
```

**롤백**:
```bash
# 전체 롤백
git reset --hard pre-migration/legacy-scripts-2026-01-26

# 또는 브랜치로
git checkout backup/pre-migration-2026-01-26
```

---

## 향후 작업

### Phase 0 이후

1. **Phase 1**: Repository 리팩토링
   - Alembic 마이그레이션 생성
   - Entity 구조 개선

2. **Phase 2**: Puller 리팩토링
   - app.py의 TODO 구현 시작
   - b.py 로직 통합

3. **Phase 3**: Merger 구현
   - 데이터 병합 로직

4. **Phase 4**: Scheduler 구현
   - app.py run 명령 완성
   - Cron 스케줄러 통합

---

## 참고 문서

- **실행 가이드**: `2_combined_migration_plan.md` - 실제 명령어 및 단계
- **전체 계획**: `1_master_plan.md` - Phase별 상세 계획
- **Phase 0 가이드**: `3_phase_0_preparation.md` - Alembic 설정
- **현황 분석**: `4_current_state_analysis.md` - 상세 구조 분석
- **계산식 참조**: `5_calculation_formulas_reference.md` - 모든 공식

---

**Last Updated**: 2026-01-26  
**Status**: ✅ Completed and Integrated  
**Execution Guide**: See `2_combined_migration_plan.md`
