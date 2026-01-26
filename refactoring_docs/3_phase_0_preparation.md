# Phase 0: Preparation - 리팩토링 준비 단계

**기간**: 1주  
**목표**: 안정적인 리팩토링을 위한 기반 구축  
**선행 조건**: `master_plan.md` 검토 완료

> ℹ️ **시작 전에**: 이 문서는 실행 가이드입니다. 전체 계획은 `master_plan.md`를 참고하세요.

---

## 목차

1. [개요](#1-개요)
2. [Alembic 설정](#2-alembic-설정)
3. [테스트 프레임워크 구축](#3-테스트-프레임워크-구축)
4. [검증 체크리스트](#4-검증-체크리스트)

---

## 1. 개요

Phase 0는 본격적인 리팩토링 전에 필수 인프라를 구축하는 단계입니다. 이 단계를 거치지 않고 리팩토링을 시작하면:

- ❌ 스키마 변경 시 롤백 불가
- ❌ 테스트 없이 변경 시 버그 발생 위험 높음

Phase 0 완료 후:

- ✅ 안전한 스키마 마이그레이션 (Alembic)
- ✅ 자동화된 테스트 (pytest)

---

## 2. Alembic 설정

### 3.1 Alembic 설치

```bash
# 필수 패키지 설치
pip install alembic

# requirements/essential.txt에 추가
echo "alembic>=1.13.0" >> requirements/essential.txt
```

### 3.2 Alembic 초기화

```bash
# Alembic 디렉토리 생성 (프로젝트 루트에서)
alembic init football_data_manager/repository/migrations

# 생성되는 구조:
# football_data_manager/repository/migrations/
# ├── versions/          # 마이그레이션 파일 저장소
# ├── env.py            # Alembic 환경 설정
# ├── script.py.mako    # 마이그레이션 템플릿
# └── alembic.ini       # Alembic 설정 파일
```

### 3.3 `alembic.ini` 설정

**파일 위치**: `football_data_manager/repository/migrations/alembic.ini`

```ini
[alembic]
# 마이그레이션 파일 경로
script_location = football_data_manager/repository/migrations

# 데이터베이스 URL (환경변수로 관리)
# 실제 URL은 env.py에서 동적으로 설정
sqlalchemy.url = 

# 파일 템플릿 설정
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# 타임존 설정
timezone = Asia/Seoul

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

### 3.4 `env.py` 설정 (Async 지원)

**파일 위치**: `football_data_manager/repository/migrations/env.py`

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 기존 Entity 클래스 import
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.players.player_entity import PlayerEntity
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
# ... (모든 Entity import)

# Alembic Config 객체
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Entity metadata
target_metadata = Base.metadata


def get_url():
    """환경변수 또는 config에서 DB URL 가져오기"""
    import os
    from football_data_manager.common.services.config.config_service import ConfigService
    
    # 환경변수 우선
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return db_url
    
    # ConfigService 사용
    config_service = ConfigService()
    db_config = config_service.get_db_config()
    return f"postgresql+asyncpg://{db_config.user}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database}"


def run_migrations_offline() -> None:
    """오프라인 모드: SQL 스크립트만 생성"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """비동기 모드: 실제 DB에 적용"""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
    
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """온라인 모드 진입점"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

### 3.5 초기 마이그레이션 생성

```bash
# 현재 스키마 캡처 (auto-generate)
alembic revision --autogenerate -m "Initial schema"

# 생성된 파일 확인
# football_data_manager/repository/migrations/versions/20260126_1430_abc123_initial_schema.py

# 마이그레이션 파일 검토 (중요!)
# - 모든 테이블이 포함되었는지 확인
# - Association 테이블 (11개) 확인
# - 인덱스 및 제약조건 확인
```

**생성된 마이그레이션 파일 예시**:

```python
"""Initial schema

Revision ID: abc123
Revises: 
Create Date: 2026-01-26 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc123'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 테이블 생성 (15개 main tables)
    op.create_table('awards',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('source', sa.Enum('PULSELIVE', 'THE_ATHLETIC', name='sourceenum'), nullable=False),
        sa.Column('source_id', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        # ... 추가 컬럼
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('source_id')
    )
    # ... (모든 테이블)


def downgrade() -> None:
    # 롤백 로직
    op.drop_table('awards')
    # ... (모든 테이블)
```

### 3.6 마이그레이션 검증 (Dry-run)

```bash
# SQL만 확인 (실제 적용 안 함)
alembic upgrade head --sql

# 출력 검토:
# - CREATE TABLE 문 확인
# - 인덱스 및 제약조건 확인
# - 순서 확인 (FK 의존성)
```

### 3.7 마이그레이션 적용 (실제 DB)

⚠️ **주의**: 프로덕션 DB에 적용하기 전에 반드시 백업!

```bash
# 개발 환경에서 먼저 테스트
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/football_dev"
alembic upgrade head

# 버전 확인
alembic current

# 출력:
# abc123 (head)
```

### 3.8 Alembic 사용법 요약

```bash
# 새 마이그레이션 생성 (auto-detect)
alembic revision --autogenerate -m "Add new column to players"

# 수동 마이그레이션 생성
alembic revision -m "Custom migration"

# 최신 버전으로 업그레이드
alembic upgrade head

# 특정 버전으로 업그레이드
alembic upgrade abc123

# 한 단계 업그레이드
alembic upgrade +1

# 한 단계 다운그레이드 (롤백)
alembic downgrade -1

# 특정 버전으로 다운그레이드
alembic downgrade abc123

# 현재 버전 확인
alembic current

# 마이그레이션 히스토리 보기
alembic history

# SQL만 출력 (적용 안 함)
alembic upgrade head --sql
```

---

## 3. 테스트 프레임워크 구축

### 4.1 pytest 설치

```bash
# 테스트 의존성 설치
pip install pytest pytest-asyncio pytest-cov

# requirements/test.txt에 추가
cat >> requirements/test.txt << EOF
pytest>=8.0.0
pytest-asyncio>=0.23.0
pytest-cov>=4.1.0
pytest-mock>=3.12.0
httpx>=0.26.0  # 이미 있을 수 있음
EOF
```

### 4.2 pytest 설정

**파일 위치**: `pyproject.toml` (이미 존재)

기존 설정 확인:
```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
addopts = ["--import-mode=importlib"]
```

**추가 설정**:
```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
addopts = [
    "--import-mode=importlib",
    "-v",                           # verbose
    "--tb=short",                   # 짧은 traceback
    "--strict-markers",             # 정의되지 않은 마커 금지
    "--asyncio-mode=auto",          # 자동 async 탐지
]
asyncio_mode = "auto"
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]

[tool.coverage.run]
source = ["football_data_manager"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/__pycache__/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
precision = 2
```

### 4.3 테스트 디렉토리 구조 정리

```bash
tests/
├── conftest.py                    # 공통 fixture
├── unit/                          # 단위 테스트
│   ├── test_repositories/
│   │   ├── test_base_repository.py
│   │   ├── test_player_repository.py
│   │   └── ...
│   ├── test_pullers/
│   └── test_mergers/
└── integration/                   # 통합 테스트
    ├── test_full_pipeline.py
    └── test_database.py
```

### 4.4 공통 Fixture 작성

**파일 위치**: `tests/conftest.py`

```python
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from football_data_manager.common.repositories import Base


@pytest.fixture(scope="session")
def event_loop():
    """Session-scoped event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_engine():
    """Test database engine (in-memory SQLite or test PostgreSQL)"""
    # 옵션 1: SQLite in-memory (빠르지만 PostgreSQL 호환성 낮음)
    # engine = create_async_engine("sqlite+aiosqlite:///:memory:", poolclass=NullPool)
    
    # 옵션 2: Test PostgreSQL (느리지만 프로덕션과 동일)
    engine = create_async_engine(
        "postgresql+asyncpg://user:pass@localhost:5432/football_test",
        poolclass=NullPool
    )
    
    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # 테이블 삭제
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """Test database session"""
    async_session = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest.fixture
def sample_player_data():
    """Sample player data for tests"""
    return {
        "source_id": "p12345",
        "display_name_en": "John Doe",
        "display_name_kr": "존 도우",
        "full_name": "Johnathan Doe",
        "nationality_en": "England",
        "nationality_kr": "잉글랜드",
        "position": "FWD",
        "preferred_foot": "RIGHT",
    }
```

### 4.5 기존 테스트 검증

```bash
# 모든 테스트 실행
pytest

# 커버리지 포함 실행
pytest --cov=football_data_manager --cov-report=html

# 커버리지 리포트 확인
open htmlcov/index.html  # macOS
# 또는 xdg-open htmlcov/index.html  # Linux
```

**예상 결과**:
```
======================== test session starts ========================
collected 42 items

tests/common/repositories/test_base_repository.py ........  [ 19%]
tests/common/repositories/test_player_repository.py ....   [ 28%]
tests/common/repositories/test_team_repository.py ....     [ 38%]
...

---------- coverage: platform darwin, python 3.12.1 -----------
Name                                          Stmts   Miss  Cover
-----------------------------------------------------------------
football_data_manager/common/repositories/...   250     50    80%
...
-----------------------------------------------------------------
TOTAL                                          1500    300    80%
```

### 4.6 Baseline 테스트 작성 (누락 시)

**파일 위치**: `tests/integration/test_database.py`

```python
import pytest
from football_data_manager.common.repositories.players.player_entity import PlayerEntity
from football_data_manager.common.repositories.players.player_repository import PlayerRepository
from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.enums.side_enum import SideEnum
from football_data_manager.common.services.db.db_service import DbService


@pytest.mark.integration
async def test_create_and_read_player(db_session, sample_player_data):
    """기본 CRUD 동작 검증"""
    # Create
    player = PlayerEntity(
        source_id=sample_player_data["source_id"],
        display_name_en=sample_player_data["display_name_en"],
        display_name_kr=sample_player_data["display_name_kr"],
        full_name=sample_player_data["full_name"],
        nationality_en=sample_player_data["nationality_en"],
        nationality_kr=sample_player_data["nationality_kr"],
        position=PositionEnum.FWD,
        preferred_foot=SideEnum.RIGHT,
        birth_country="England",
        birth_date=None,
    )
    
    db_session.add(player)
    await db_session.commit()
    
    # Read
    result = await db_session.get(PlayerEntity, player.id)
    
    assert result is not None
    assert result.display_name_en == "John Doe"
    assert result.position == PositionEnum.FWD


@pytest.mark.integration
async def test_alembic_current_schema(db_engine):
    """Alembic 스키마와 현재 모델 일치 확인"""
    from alembic.config import Config
    from alembic import command
    from alembic.script import ScriptDirectory
    from alembic.runtime.migration import MigrationContext
    
    # Alembic config
    alembic_cfg = Config("football_data_manager/repository/migrations/alembic.ini")
    
    # 현재 스키마 버전 확인
    async with db_engine.begin() as conn:
        context = await conn.run_sync(
            lambda sync_conn: MigrationContext.configure(sync_conn)
        )
        current_rev = context.get_current_revision()
    
    # 최신 마이그레이션 버전 확인
    script = ScriptDirectory.from_config(alembic_cfg)
    head_rev = script.get_current_head()
    
    assert current_rev == head_rev, f"Schema mismatch: DB={current_rev}, Head={head_rev}"
```

---

## 4. 검증 체크리스트

### 4.1 Alembic 검증

- [ ] `alembic.ini` 설정 완료
- [ ] `env.py` async 설정 완료
- [ ] 초기 마이그레이션 생성 (`alembic revision --autogenerate`)
- [ ] 마이그레이션 SQL 검토 (`alembic upgrade head --sql`)
- [ ] 개발 DB에 마이그레이션 적용 (`alembic upgrade head`)
- [ ] `alembic current` 확인 (버전 출력)
- [ ] 모든 테이블 생성 확인 (15개 main + 11개 association)
- [ ] 롤백 테스트 (`alembic downgrade -1` → `alembic upgrade head`)

### 4.2 테스트 프레임워크 검증

- [ ] pytest 설치 확인 (`pytest --version`)
- [ ] `pyproject.toml` 설정 추가
- [ ] `tests/conftest.py` fixture 작성
- [ ] 기존 테스트 실행 (`pytest`)
- [ ] 모든 테스트 통과
- [ ] 커버리지 80% 이상 (`pytest --cov`)
- [ ] Integration test 작성 (최소 1개)
- [ ] Alembic 스키마 일치 테스트 작성

### 5.4 문서화

- [ ] `README.md`에 Alembic 사용법 추가
- [ ] `README.md`에 테스트 실행법 추가
- [ ] `README.md`에 백업/복원 가이드 추가
- [ ] Phase 0 완료 보고서 작성

---

## 5. Phase 0 완료 기준

다음 조건을 **모두** 만족해야 Phase 1로 진행 가능:

1. ✅ Alembic 초기 마이그레이션 생성 및 적용 완료
2. ✅ `alembic current` 명령으로 버전 확인 가능
3. ✅ 모든 기존 테스트 통과 (`pytest`)
4. ✅ 커버리지 80% 이상 달성

**실패 시**: 위 조건 중 하나라도 실패하면 Phase 1 진행 불가.

---

## 6. 다음 단계

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
