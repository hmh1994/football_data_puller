# Phase 0: Preparation - 리팩토링 준비 단계

**상태**: ✅ 완료 (2026-02-01)
**목표**: Alembic 마이그레이션 설정
**선행 조건**: `4_combined_migration_plan.md` 실행 완료 ✅

> ℹ️ **시작 전에**: 이 문서는 실행 가이드입니다. 전체 계획은 `1_master_plan.md`를 참고하세요.

---

## 목차

1. [개요](#1-개요)
2. [Alembic 설정](#2-alembic-설정)
   - 2.1 Alembic 설치
   - 2.2 Alembic 초기화
   - 2.3 alembic.ini 설정
   - 2.4 env.py 설정 (ConfigService 연동)
3. [검증 체크리스트](#3-검증-체크리스트)
4. [Phase 0 완료 기준](#4-phase-0-완료-기준)
5. [다음 단계](#5-다음-단계)

---

## 1. 개요

Phase 0는 본격적인 리팩토링 전에 필수 인프라를 구축하는 단계입니다. 이 단계를 거치지 않고 리팩토링을 시작하면:

- ❌ 스키마 변경 시 롤백 불가

Phase 0 완료 후:

- ✅ 안전한 스키마 마이그레이션 (Alembic)

> ℹ️ **테스트 프레임워크**: 기존 테스트는 리팩토링 과정에서 수정 예정이므로 Phase 0에서 제외합니다.

---

## 2. Alembic 설정

### 2.1 Alembic 설치

```bash
# 필수 패키지 설치
pip install alembic

# requirements/essential.txt에 추가
# alembic>=1.13.0
```

**실행 결과**: Alembic 1.18.3 설치 완료, `requirements/essential.txt`에 `alembic>=1.13.0` 추가 완료

### 2.2 Alembic 초기화

```bash
# Alembic 디렉토리 생성 (프로젝트 루트에서)
alembic init football_data_manager/migrations

# 생성된 구조:
# football_data_manager/migrations/
# ├── versions/          # 마이그레이션 파일 저장소
# ├── env.py            # Alembic 환경 설정
# ├── script.py.mako    # 마이그레이션 템플릿
# └── README
# alembic.ini            # 프로젝트 루트에 생성됨
```

**실행 결과**: 디렉토리 구조 생성 완료

### 2.3 `alembic.ini` 설정

**파일 위치**: 프로젝트 루트 `alembic.ini`

```ini
[alembic]
# 마이그레이션 파일 경로
script_location = %(here)s/football_data_manager/migrations

# 파일 템플릿 설정 (날짜 기반)
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# sys.path 설정
prepend_sys_path = .

# 경로 구분자
path_separator = os

# 데이터베이스 URL (env.py에서 동적으로 설정)
sqlalchemy.url =
```

**실행 결과**: 설정 완료

### 2.4 `env.py` 설정 (Async 지원)

**파일 위치**: `football_data_manager/migrations/env.py`

```python
import asyncio
import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Entity imports (15 entities)
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.analytics.analytics_entity import AnalyticsEntity
from football_data_manager.common.repositories.awards.award_entity import AwardEntity
# ... (15개 엔티티 + 11개 어소시에이션 전체 import)

# Alembic Config 객체
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Entity metadata
target_metadata = Base.metadata


def get_url() -> str:
    """환경변수 또는 ConfigService에서 DB URL 가져오기"""
    # 환경변수 우선
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url

    # ConfigService 사용
    from football_data_manager.common.services.config.config_service import ConfigService

    config_path = Path(os.getenv("CONFIG_PATH", "./configs/.env"))
    config_service = ConfigService(config_path=config_path)
    return str(config_service.db.sqlalchemy_url)
```

**핵심 사항**:
- `ConfigService(config_path=Path)` 생성자 사용 (인자 없는 생성자 아님)
- `config_service.db.sqlalchemy_url` 프로퍼티로 URL 접근
- 환경변수 `DATABASE_URL` 우선, 없으면 ConfigService 사용
- 15개 Entity + 11개 Association = 총 26개 테이블 import

**실행 결과**: env.py 작성 완료, 26개 테이블 등록 확인

---

## 3. 검증 체크리스트

### 3.1 Alembic 설정 검증

- [x] `alembic.ini` 파일 존재 및 설정 완료 (프로젝트 루트)
- [x] `env.py` async 설정 완료 (`run_async_migrations()`)
- [x] `get_url()` 함수가 ConfigService에서 DB 설정 읽어오기 성공
- [x] `target_metadata = Base.metadata` 설정 확인
- [x] 모든 Entity import 확인 (15 entities + 11 associations = 26 tables)

### 3.2 추가 작업 (Phase 0 범위 내)

- [x] `football_data_manager/` 최소 구조 생성 (archive에서 entity/association 복원)
- [x] `*_repository.py` 제거 (재구성 방해 방지)
- [x] Entity 비즈니스 로직 메서드 제거 (스키마 정의만 유지)
- [x] Entity docstring 점검 및 수정

---

## 4. Phase 0 완료 기준

다음 조건을 **모두** 만족해야 Phase 1로 진행 가능:

1. ✅ Alembic 설정 완료 (`alembic.ini`, `env.py`)
2. ✅ ConfigService에서 DB 설정 읽어오기 성공
3. ✅ 26개 테이블 등록 확인

**다음 단계**: Phase 1부터 각 리팩토링 작업 시 필요에 따라 마이그레이션 생성 및 적용

---

## 5. 다음 단계

Phase 0 완료 후:

1. **Phase 1 계획 문서 읽기**: `phase_1_repository.md`
2. **Repository 리팩토링 시작**
3. **각 단계마다 테스트 및 마이그레이션 생성**

---

## Appendix A: 트러블슈팅

### A.1 Alembic: "Can't locate revision identified by 'head'"

**원인**: 마이그레이션 파일이 없음

**해결**:

```bash
alembic revision --autogenerate -m "Initial schema"
```

### A.2 Alembic: "Target database is not up to date"

**원인**: 현재 DB 버전과 코드 버전 불일치

**해결**:

```bash
# 현재 버전 확인
alembic current

# 최신 버전으로 업그레이드
alembic upgrade head
```

### A.3 pytest: "ImportError: No module named 'football_data_manager'"

**원인**: PYTHONPATH 설정 안 됨

**해결**:

```bash
# pyproject.toml 확인
[tool.pytest.ini_options]
pythonpath = ["."]

# 또는 환경변수 설정
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### A.4 pg_dump: "role does not exist"

**원인**: PostgreSQL 사용자 권한 문제

**해결**:

```bash
# PostgreSQL 사용자 생성
psql -U postgres -c "CREATE USER myuser WITH PASSWORD 'mypassword';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE football_data TO myuser;"
```

---

**Document End**
