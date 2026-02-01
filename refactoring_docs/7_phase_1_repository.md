# Phase 1: Repository 리팩토링

**상태**: 완료 ✅
**목표**: Repository 컴포넌트 전면 재구성 (Entity + Repository + Session + Container)
**선행 조건**: Phase 0 완료 ✅

> **시작 전에**: 이 문서는 실행 가이드입니다. 전체 계획은 `1_master_plan.md`를 참고하세요.

---

## 목차

1. [개요](#1-개요)
2. [Step 1: 초기 Alembic 마이그레이션](#2-step-1-초기-alembic-마이그레이션)
3. [Step 2: 디렉토리 구조 생성](#3-step-2-디렉토리-구조-생성)
4. [Step 3: Base 클래스 마이그레이션 (SQLAlchemy 2.0)](#4-step-3-base-클래스-마이그레이션-sqlalchemy-20)
5. [Step 4: Entity 마이그레이션](#5-step-4-entity-마이그레이션)
6. [Step 5: Session Factory 구현](#6-step-5-session-factory-구현)
7. [Step 6: AsyncBaseRepository 구현](#7-step-6-asyncbaserepository-구현)
8. [Step 7: 개별 Repository 구현](#8-step-7-개별-repository-구현)
9. [Step 8: RepositoryContainer 구현](#9-step-8-repositorycontainer-구현)
10. [Step 9: Alembic 재설정](#10-step-9-alembic-재설정)
11. [Step 10: 검증](#11-step-10-검증)
12. [검증 체크리스트](#12-검증-체크리스트)
13. [Phase 1 완료 기준](#13-phase-1-완료-기준)
14. [다음 단계](#14-다음-단계)

---

## 1. 개요

### 1.1 Phase 1 범위

Phase 1은 Repository 컴포넌트를 전면 재구성하는 단계입니다:

- **Entity 마이그레이션**: 현재 `common/repositories/` → 새로운 `repository/entities/`
- **SQLAlchemy 2.0 스타일 적용**: `declarative_base()` → `DeclarativeBase`, `Column` → `Mapped[T]`
- **AsyncBaseRepository 구현**: 새로운 제네릭 Repository 베이스 클래스
- **개별 Repository 재구현**: archive 참조하여 특수 메서드 포함 재작성
- **Session Factory**: `DbService` 대체
- **DI Container**: `RepositoryContainer` 재구현

### 1.2 현재 상태 (Phase 0 완료 후)

```
football_data_manager/
├── common/
│   ├── enums/                    # 8개 Enum ✅ 유지
│   ├── repositories/             # Entity + Association만 존재 (Repository 없음)
│   │   ├── __init__.py           # Base (declarative_base, AlchemyABCMeta)
│   │   ├── base_entity.py        # BaseEntity (스키마만)
│   │   ├── pulselive_entity.py   # PulseliveEntity (스키마만)
│   │   ├── constants.py          # 테이블명 상수
│   │   ├── analytics/            # AnalyticsEntity
│   │   ├── awards/               # AwardEntity
│   │   ├── competitions/         # CompetitionEntity
│   │   ├── fixtures/             # FixtureEntity
│   │   ├── grounds/              # GroundEntity
│   │   ├── match_stats/          # MatchStatEntity
│   │   ├── matches/              # MatchEntity + 5 Associations
│   │   ├── news/                 # NewsEntity + 1 Association
│   │   ├── officials/            # OfficialEntity
│   │   ├── player_stats/         # PlayerStatEntity + 1 Association
│   │   ├── players/              # PlayerEntity + 1 Association
│   │   ├── seasons/              # SeasonEntity
│   │   ├── staffs/               # StaffEntity + 1 Association
│   │   ├── team_stats/           # TeamStatEntity + 1 Association
│   │   └── teams/                # TeamEntity + 1 Association
│   ├── services/
│   │   ├── config/               # ConfigService ✅ 유지
│   │   └── db/                   # 비어있음 (DbService는 archive에)
│   └── utils/                    # 유틸리티 ✅ 유지
└── migrations/                   # Alembic ✅ 유지
```

### 1.3 Phase 1 완료 후 목표 구조

```
football_data_manager/
├── repository/                   # ★ 새로 생성
│   ├── __init__.py
│   ├── entities/                 # Entity 정의
│   │   ├── __init__.py           # Base, BaseEntity export
│   │   ├── base.py               # DeclarativeBase, BaseEntity, PulseliveEntity
│   │   ├── analytics.py          # AnalyticsEntity
│   │   ├── awards.py             # AwardEntity
│   │   ├── competitions.py       # CompetitionEntity
│   │   ├── fixtures.py           # FixtureEntity
│   │   ├── grounds.py            # GroundEntity
│   │   ├── match_stats.py        # MatchStatEntity
│   │   ├── matches.py            # MatchEntity + 5 Associations
│   │   ├── news.py               # NewsEntity + NewsTeamAssociation
│   │   ├── officials.py          # OfficialEntity
│   │   ├── player_stats.py       # PlayerStatEntity + PlayerStatAwardAssociation
│   │   ├── players.py            # PlayerEntity + PlayerChampionshipAssociation
│   │   ├── seasons.py            # SeasonEntity
│   │   ├── staffs.py             # StaffEntity + StaffAwardAssociation
│   │   ├── team_stats.py         # TeamStatEntity + TeamStatMatchAssociation
│   │   └── teams.py              # TeamEntity + TeamChampionshipAssociation
│   ├── repositories/             # Repository 구현
│   │   ├── __init__.py
│   │   ├── base.py               # AsyncBaseRepository
│   │   ├── pulselive.py          # PulseliveRepository
│   │   ├── analytics.py
│   │   ├── awards.py
│   │   ├── competitions.py
│   │   ├── fixtures.py
│   │   ├── grounds.py
│   │   ├── match_stats.py
│   │   ├── matches.py
│   │   ├── news.py
│   │   ├── officials.py
│   │   ├── player_stats.py
│   │   ├── players.py
│   │   ├── seasons.py
│   │   ├── staffs.py
│   │   ├── team_stats.py
│   │   └── teams.py
│   ├── session.py                # AsyncSession Factory
│   └── container.py              # RepositoryContainer (DI)
├── common/
│   ├── enums/                    # ✅ 유지
│   ├── services/config/          # ✅ 유지
│   └── utils/                    # ✅ 유지
└── migrations/                   # Alembic (env.py 업데이트 필요)
```

### 1.4 핵심 변경 사항

| 항목 | 현재 | Phase 1 이후 |
|------|------|-------------|
| Base 클래스 | `declarative_base()` + `AlchemyABCMeta` | `DeclarativeBase` (SQLAlchemy 2.0) |
| Column 정의 | `Column(String, ...)` | `Mapped[str]` + `mapped_column(...)` |
| Session 관리 | `DbService` + `@with_db_session` 데코레이터 | `async_sessionmaker` + context manager |
| Repository | `BaseRepository[T]` + `PulseliveRepository[T]` | `AsyncBaseRepository[T]` + `PulseliveRepository[T]` |
| Entity 위치 | `common/repositories/<domain>/` | `repository/entities/` |
| Association 위치 | 각 도메인 폴더 별도 파일 | Entity와 동일 파일 |

---

## 2. Step 1: 초기 Alembic 마이그레이션

현재 DB 스키마의 스냅샷을 Alembic으로 기록합니다. 이후 Entity 변경 시 안전하게 마이그레이션할 수 있습니다.

### 2.1 마이그레이션 생성

```bash
# 프로젝트 루트에서 실행
alembic revision --autogenerate -m "Initial schema snapshot"
```

### 2.2 생성된 파일 확인

```bash
# versions/ 디렉토리에 새 파일 생성됨
ls football_data_manager/migrations/versions/

# 마이그레이션 파일 내용 확인 (26개 테이블이 포함되어야 함)
```

### 2.3 마이그레이션 적용

```bash
# 현재 DB에 적용 (기존 테이블이 이미 있으므로 stamp으로 기록만)
alembic stamp head
```

> **참고**: 기존 DB에 테이블이 이미 존재하므로 `stamp head`로 현재 상태를 기록만 합니다. `upgrade head`를 실행하면 이미 존재하는 테이블 생성을 시도하여 오류가 발생합니다.

---

## 3. Step 2: 디렉토리 구조 생성

### 3.1 새로운 디렉토리 생성

```bash
# repository 패키지
mkdir -p football_data_manager/repository/entities
mkdir -p football_data_manager/repository/repositories

# __init__.py 생성
touch football_data_manager/repository/__init__.py
touch football_data_manager/repository/entities/__init__.py
touch football_data_manager/repository/repositories/__init__.py
```

### 3.2 디렉토리 확인

```
football_data_manager/repository/
├── __init__.py
├── entities/
│   └── __init__.py
├── repositories/
│   └── __init__.py
├── session.py          # Step 5에서 생성
└── container.py        # Step 8에서 생성
```

---

## 4. Step 3: Base 클래스 마이그레이션 (SQLAlchemy 2.0)

현재 `common/repositories/__init__.py`의 `declarative_base()` 패턴을 SQLAlchemy 2.0의 `DeclarativeBase`로 전환합니다.

### 4.1 현재 상태

```python
# common/repositories/__init__.py (현재)
from abc import ABCMeta
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

class AlchemyABCMeta(DeclarativeMeta, ABCMeta):
    pass

Base = declarative_base(metaclass=AlchemyABCMeta)
```

### 4.2 새로운 Base 정의

**파일**: `repository/entities/base.py`

```python
from uuid import uuid4

from sqlalchemy import String, DateTime, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base class."""
    pass


class BaseEntity(Base):
    """
    Base entity model.

    All entities inherit from this class, which provides common fields
    for identification, source tracking, and timestamps.

    :ivar id: Unique identifier (UUID)
    :ivar source: Data source identifier
    :ivar source_id: Unique identifier from the source
    :ivar created_at: Creation timestamp (UTC)
    :ivar updated_at: Last modification timestamp (UTC)
    """

    __abstract__ = True

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source: Mapped[SourceEnum] = mapped_column(Enum(SourceEnum), nullable=False)
    source_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    def __init__(
        self,
        source: SourceEnum,
        source_id: str,
        **kwargs,
    ):
        """
        Initialize the base entity.

        :param source: Source of the entity data
        :param source_id: Unique identifier from the source
        :param kwargs: Additional keyword arguments
        """
        now = create_utc_now()
        super().__init__(**kwargs)
        self.id = str(uuid4())
        self.created_at = now
        self.source = source
        self.source_id = source_id
        self.updated_at = now


class PulseliveEntity(BaseEntity):
    """
    Pulselive entity model.

    Abstract base for entities sourced from the Pulselive API.
    Automatically sets source to PULSELIVE.
    """

    __abstract__ = True

    def __init__(self, source_id: str, **kwargs):
        """
        Initialize the Pulselive entity.

        :param source_id: Unique identifier from the source
        """
        super().__init__(
            source=SourceEnum.PULSELIVE,
            source_id=source_id,
            **kwargs,
        )
```

### 4.3 핵심 변경 포인트

| 항목 | 이전 | 이후 |
|------|------|------|
| Base 생성 | `declarative_base(metaclass=AlchemyABCMeta)` | `class Base(DeclarativeBase)` |
| ABCMeta 합성 | `AlchemyABCMeta(DeclarativeMeta, ABCMeta)` | 불필요 (DeclarativeBase가 처리) |
| Column 정의 | `Column(String, nullable=False)` | `Mapped[str] = mapped_column(String, ...)` |
| import 경로 | `sqlalchemy.ext.declarative` | `sqlalchemy.orm` |

> **주의**: `DeclarativeBase`는 `ABCMeta`와의 메타클래스 충돌 없이 `__abstract__ = True`를 지원합니다. 별도의 메타클래스 합성이 불필요합니다.

### 4.4 `Mapped[T]` 타입 매핑 참조

| SQLAlchemy Column | Mapped 타입 | 예시 |
|-------------------|------------|------|
| `Column(String)` | `Mapped[str]` | `id: Mapped[str] = mapped_column(String, ...)` |
| `Column(Integer)` | `Mapped[int]` | `attendance: Mapped[int] = mapped_column(Integer, ...)` |
| `Column(Boolean)` | `Mapped[bool]` | `is_home: Mapped[bool] = mapped_column(Boolean, ...)` |
| `Column(DateTime)` | `Mapped[DateTime]` | `created_at: Mapped[DateTime] = mapped_column(...)` |
| `Column(Enum(...))` | `Mapped[EnumType]` | `source: Mapped[SourceEnum] = mapped_column(...)` |
| `Column(ARRAY(Integer))` | `Mapped[list[int]]` | `formation: Mapped[list[int]] = mapped_column(ARRAY(Integer), ...)` |
| Nullable column | `Mapped[T \| None]` | `photo_url: Mapped[str \| None] = mapped_column(...)` |

---

## 5. Step 4: Entity 마이그레이션

각 Entity를 새 위치로 이동하고 SQLAlchemy 2.0 스타일로 변환합니다. Association은 해당 Entity 파일에 함께 정의합니다.

### 5.1 파일 매핑

| 현재 경로 | 새 경로 | 포함 내용 |
|----------|---------|----------|
| `common/repositories/base_entity.py` | `repository/entities/base.py` | Base, BaseEntity, PulseliveEntity |
| `common/repositories/pulselive_entity.py` | `repository/entities/base.py` | (위에 통합) |
| `common/repositories/analytics/analytics_entity.py` | `repository/entities/analytics.py` | AnalyticsEntity |
| `common/repositories/awards/award_entity.py` | `repository/entities/awards.py` | AwardEntity |
| `common/repositories/competitions/competition_entity.py` | `repository/entities/competitions.py` | CompetitionEntity |
| `common/repositories/fixtures/fixture_entity.py` | `repository/entities/fixtures.py` | FixtureEntity |
| `common/repositories/grounds/ground_entity.py` | `repository/entities/grounds.py` | GroundEntity |
| `common/repositories/match_stats/match_stat_entity.py` | `repository/entities/match_stats.py` | MatchStatEntity |
| `common/repositories/matches/match_entity.py` + 5 associations | `repository/entities/matches.py` | MatchEntity + 5 Associations |
| `common/repositories/news/news_entity.py` + 1 association | `repository/entities/news.py` | NewsEntity + NewsTeamAssociation |
| `common/repositories/officials/official_entity.py` | `repository/entities/officials.py` | OfficialEntity |
| `common/repositories/player_stats/player_stat_entity.py` + 1 association | `repository/entities/player_stats.py` | PlayerStatEntity + PlayerStatAwardAssociation |
| `common/repositories/players/player_entity.py` + 1 association | `repository/entities/players.py` | PlayerEntity + PlayerChampionshipAssociation |
| `common/repositories/seasons/season_entity.py` | `repository/entities/seasons.py` | SeasonEntity |
| `common/repositories/staffs/staff_entity.py` + 1 association | `repository/entities/staffs.py` | StaffEntity + StaffAwardAssociation |
| `common/repositories/team_stats/team_stat_entity.py` + 1 association | `repository/entities/team_stats.py` | TeamStatEntity + TeamStatMatchAssociation |
| `common/repositories/teams/team_entity.py` + 1 association | `repository/entities/teams.py` | TeamEntity + TeamChampionshipAssociation |

### 5.2 변환 예시: PlayerEntity

**현재** (`common/repositories/players/player_entity.py`):

```python
from sqlalchemy import Column, String, Integer, Float, ForeignKey, Date, Enum
from football_data_manager.common.repositories.pulselive_entity import PulseliveEntity

class PlayerEntity(PulseliveEntity):
    __tablename__ = PLAYERS_TABLE_NAME

    display_name_en = Column(String, nullable=False)
    display_name_kr = Column(String, nullable=True)
    position = Column(Enum(PositionEnum), nullable=True)
    height = Column(Integer, nullable=True)
    ...
```

**Phase 1 이후** (`repository/entities/players.py`):

```python
from sqlalchemy import String, Integer, ForeignKey, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.repository.entities.base import PulseliveEntity

PLAYERS_TABLE_NAME = "players"
PLAYER_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME = "player_championship_association"


class PlayerEntity(PulseliveEntity):
    """
    Entity model for football players.

    :ivar display_name_en: English display name
    :ivar display_name_kr: Korean display name
    :ivar position: Playing position
    :ivar height: Height in centimeters
    ...
    """

    __tablename__ = PLAYERS_TABLE_NAME

    display_name_en: Mapped[str] = mapped_column(String, nullable=False)
    display_name_kr: Mapped[str | None] = mapped_column(String, nullable=True)
    position: Mapped[PositionEnum | None] = mapped_column(
        Enum(PositionEnum), nullable=True
    )
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ...

    def __init__(self, ...):
        """기존 __init__ 로직 유지"""
        super().__init__(source_id=source_id)
        ...


class PlayerChampionshipAssociation(Base):
    """Player championship season association."""

    __tablename__ = PLAYER_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME

    ...
```

### 5.3 변환 작업 순서

의존 관계를 고려한 변환 순서:

1. **base.py**: Base, BaseEntity, PulseliveEntity (의존 없음)
2. **competitions.py**: CompetitionEntity (의존 없음)
3. **grounds.py**: GroundEntity (의존 없음)
4. **teams.py**: TeamEntity + TeamChampionshipAssociation
5. **players.py**: PlayerEntity + PlayerChampionshipAssociation
6. **officials.py**: OfficialEntity
7. **staffs.py**: StaffEntity + StaffAwardAssociation
8. **seasons.py**: SeasonEntity (CompetitionEntity FK)
9. **awards.py**: AwardEntity
10. **fixtures.py**: FixtureEntity (SeasonEntity, TeamEntity, GroundEntity FK)
11. **matches.py**: MatchEntity + 5 Associations (FixtureEntity 등 다수 FK)
12. **match_stats.py**: MatchStatEntity (MatchEntity, TeamEntity FK)
13. **player_stats.py**: PlayerStatEntity + PlayerStatAwardAssociation
14. **team_stats.py**: TeamStatEntity + TeamStatMatchAssociation
15. **news.py**: NewsEntity + NewsTeamAssociation
16. **analytics.py**: AnalyticsEntity (SeasonEntity FK)

### 5.4 `constants.py` 처리

현재 `common/repositories/constants.py`에 정의된 테이블명 상수는 각 Entity 파일로 이동합니다:

```python
# 현재: common/repositories/constants.py
PLAYERS_TABLE_NAME = "players"
TEAMS_TABLE_NAME = "teams"
...

# Phase 1 이후: 각 entity 파일의 모듈 상수로 이동
# repository/entities/players.py
PLAYERS_TABLE_NAME = "players"
PLAYER_CHAMPIONSHIP_ASSOCIATION_TABLE_NAME = "player_championship_association"
```

### 5.5 `__init__` 메서드 유지

Entity의 `__init__` 메서드는 현재 로직을 그대로 유지합니다. `__init__`에서 FK ID 할당, 기본값 설정 등의 로직이 있으므로 제거하지 않습니다.

---

## 6. Step 5: Session Factory 구현

기존 `DbService`를 대체하는 가벼운 세션 팩토리입니다.

### 6.1 구현

**파일**: `repository/session.py`

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from football_data_manager.common.services.config.config_service import ConfigService


class SessionFactory:
    """
    Async database session factory.

    Manages the AsyncEngine lifecycle and provides sessions via context manager.

    :ivar engine: SQLAlchemy async engine
    """

    engine: AsyncEngine

    def __init__(self, config_service: ConfigService):
        """
        Initialize the session factory.

        :param config_service: Configuration service for DB URL
        """
        self.engine = create_async_engine(
            config_service.db.sqlalchemy_url,
            pool_pre_ping=True,
        )
        self._session_maker = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Create a database session with automatic commit/rollback.

        :return: AsyncSession instance
        """
        async with self._session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def check_connection(self) -> bool:
        """
        Check database connectivity.

        :return: True if connection successful
        """
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
```

### 6.2 기존 `DbService`와의 차이

| 항목 | DbService (기존) | SessionFactory (신규) |
|------|-----------------|---------------------|
| Session 생성 | `sessionmaker` (deprecated) | `async_sessionmaker` (SQLAlchemy 2.0) |
| Session 메서드 | `create_db_session()` | `session()` |
| 세션 종료 | 명시적 `close()` | `async_sessionmaker`가 자동 관리 |

---

## 7. Step 6: AsyncBaseRepository 구현

기존 `BaseRepository`를 현대화한 새로운 베이스 클래스입니다.

### 7.1 설계 원칙

- **세션 주입**: `@with_db_session` 데코레이터 대신 context manager 패턴 사용
- **제네릭 타입**: `Generic[TEntity]` 유지
- **기존 메서드 보존**: CRUD + count/exists + 유틸리티 메서드 전부 유지
- **Deduplication**: `__sieve_duplication` 로직 유지

### 7.2 구현

**파일**: `repository/repositories/base.py`

```python
from typing import TypeVar, Generic, Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.repository.entities.base import BaseEntity
from football_data_manager.repository.session import SessionFactory
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)
from football_data_manager.common.utils.type_helper.list_helper import (
    remove_duplicates,
)

TEntity = TypeVar("TEntity", bound=BaseEntity)


class AsyncBaseRepository(Generic[TEntity]):
    """
    Async base repository with generic CRUD operations.

    Provides standard database operations for any entity type.
    All methods accept an optional session parameter; if not provided,
    a new session is created from the session factory.

    :param session_factory: Factory for creating database sessions
    :param model: SQLAlchemy model class for this repository
    """

    def __init__(self, session_factory: SessionFactory, model: type[TEntity]):
        self._session_factory = session_factory
        self._model = model

    # ── Create ──────────────────────────────────────────────

    async def create(
        self, entity: TEntity, session: AsyncSession | None = None
    ) -> TEntity | None:
        """
        Create an entity. Returns None if duplicate.

        :param entity: Entity to create
        :param session: Optional existing session
        :return: Created entity or None if duplicate
        """
        async def _do(s: AsyncSession) -> TEntity | None:
            if await self._sieve_duplication(s, entity) is None:
                return None
            s.add(entity)
            await s.flush()
            await s.refresh(entity)
            return entity

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def create_many(
        self, entities: Sequence[TEntity], session: AsyncSession | None = None
    ) -> list[TEntity]:
        """
        Create multiple entities with deduplication.

        :param entities: Entities to create
        :param session: Optional existing session
        :return: Successfully created entities
        """
        async def _do(s: AsyncSession) -> list[TEntity]:
            unique = remove_duplicates(
                remove_duplicates(list(entities), key=lambda e: e.id),
                key=lambda e: (e.source, e.source_id),
            )
            sieved = [await self._sieve_duplication(s, e) for e in unique]
            candidates = [e for e in sieved if e is not None]
            if candidates:
                s.add_all(candidates)
                await s.flush()
            return candidates

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    # ── Read ────────────────────────────────────────────────

    async def get_by_id(
        self, entity_id: str, session: AsyncSession | None = None
    ) -> TEntity | None:
        """
        Get entity by primary key.

        :param entity_id: Entity UUID
        :param session: Optional existing session
        :return: Entity or None
        """
        async def _do(s: AsyncSession) -> TEntity | None:
            return await s.get(self._model, entity_id)

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def get_by_source(
        self,
        source: SourceEnum,
        source_id: str,
        session: AsyncSession | None = None,
    ) -> TEntity | None:
        """
        Get entity by source and source_id.

        :param source: Data source enum
        :param source_id: Source-specific ID
        :param session: Optional existing session
        :return: Entity or None
        """
        async def _do(s: AsyncSession) -> TEntity | None:
            stmt = (
                select(self._model)
                .filter_by(
                    source=(
                        source.value.upper()
                        if isinstance(source, SourceEnum)
                        else source.upper()
                    )
                )
                .filter_by(source_id=str(source_id))
            )
            result = await s.execute(stmt)
            return result.scalars().first()

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def get_all(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
        session: AsyncSession | None = None,
    ) -> list[TEntity]:
        """
        Get all entities with optional pagination.

        :param limit: Maximum number of results
        :param offset: Number of results to skip
        :param session: Optional existing session
        :return: List of entities
        """
        async def _do(s: AsyncSession) -> list[TEntity]:
            stmt = select(self._model).offset(offset)
            if limit is not None:
                stmt = stmt.limit(limit)
            result = await s.execute(stmt)
            return list(result.unique().scalars().all())

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def count(
        self, *filters, session: AsyncSession | None = None
    ) -> int:
        """
        Count entities with optional filters.

        :param filters: SQLAlchemy filter expressions
        :param session: Optional existing session
        :return: Number of matching entities
        """
        async def _do(s: AsyncSession) -> int:
            stmt = select(func.count()).select_from(self._model)
            if filters:
                stmt = stmt.where(*filters)
            result = await s.execute(stmt)
            return result.scalar_one()

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def exists(
        self, entity_id: str, session: AsyncSession | None = None
    ) -> bool:
        """
        Check if entity exists by ID.

        :param entity_id: Entity UUID
        :param session: Optional existing session
        :return: True if exists
        """
        return await self.get_by_id(entity_id, session=session) is not None

    async def exists_by_source(
        self,
        source: SourceEnum,
        source_id: str,
        session: AsyncSession | None = None,
    ) -> bool:
        """
        Check if entity exists by source.

        :param source: Data source enum
        :param source_id: Source-specific ID
        :param session: Optional existing session
        :return: True if exists
        """
        return await self.get_by_source(source, source_id, session=session) is not None

    # ── Update ──────────────────────────────────────────────

    async def update(
        self, entity: TEntity, session: AsyncSession | None = None
    ) -> TEntity:
        """
        Update an entity. Sets updated_at to current UTC time.

        :param entity: Entity to update
        :param session: Optional existing session
        :return: Updated entity
        """
        async def _do(s: AsyncSession) -> TEntity:
            entity.updated_at = create_utc_now()
            merged = await s.merge(entity)
            await s.flush()
            await s.refresh(merged)
            return merged

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    # ── Delete ──────────────────────────────────────────────

    async def delete(
        self, entity: TEntity, session: AsyncSession | None = None
    ) -> None:
        """
        Delete an entity.

        :param entity: Entity to delete
        :param session: Optional existing session
        """
        async def _do(s: AsyncSession) -> None:
            real = await s.get(self._model, entity.id)
            if real is not None:
                await s.delete(real)
                await s.flush()

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def delete_by_id(
        self, entity_id: str, session: AsyncSession | None = None
    ) -> bool:
        """
        Delete an entity by ID.

        :param entity_id: Entity UUID
        :param session: Optional existing session
        :return: True if entity was deleted
        """
        async def _do(s: AsyncSession) -> bool:
            entity = await s.get(self._model, entity_id)
            if entity is not None:
                await s.delete(entity)
                await s.flush()
                return True
            return False

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    # ── Protected Helpers ───────────────────────────────────

    async def _get_by_field(
        self, session: AsyncSession, **kwargs
    ) -> list[TEntity]:
        """
        Get entities by field values.

        :param session: Database session
        :param kwargs: Field name-value pairs
        :return: Matching entities
        """
        stmt = select(self._model).filter_by(**kwargs)
        result = await session.execute(stmt)
        return list(result.unique().scalars().all())

    async def _get_one_by_field(self, **kwargs) -> TEntity | None:
        """
        Get single entity by field values.

        :param kwargs: Field name-value pairs
        :return: Entity or None
        """
        async with self._session_factory.session() as s:
            results = await self._get_by_field(s, **kwargs)
            return results[0] if results else None

    async def _load_lazy_fields(
        self,
        entity: TEntity,
        fields: list[str],
        session: AsyncSession | None = None,
    ) -> TEntity:
        """
        Load lazy-loaded relationship fields.

        :param entity: Entity to load fields for
        :param fields: Relationship attribute names
        :param session: Optional existing session
        :return: Entity with relationships loaded
        """
        async def _do(s: AsyncSession) -> TEntity:
            if await self.exists(entity.id, session=s):
                merged = await s.merge(entity)
                await s.refresh(merged, attribute_names=fields)
                return merged
            return entity

        if session:
            return await _do(session)
        async with self._session_factory.session() as s:
            return await _do(s)

    async def _sieve_duplication(
        self, session: AsyncSession, entity: TEntity
    ) -> TEntity | None:
        """
        Check for duplicate entity by ID and source.

        :param session: Database session
        :param entity: Entity to check
        :return: Entity if not duplicate, None otherwise
        """
        if await self.get_by_id(entity.id, session=session) is not None:
            return None
        if await self.get_by_source(
            entity.source, entity.source_id, session=session
        ) is not None:
            return None
        return entity
```

### 7.3 기존 `@with_db_session` 대비 개선 포인트

| 항목 | 기존 패턴 | 새 패턴 |
|------|----------|---------|
| 세션 제공 | 데코레이터가 첫 번째 인자 검사 | `session` 키워드 인자 (명시적) |
| 세션 관리 | `DbService.create_db_session()` | `SessionFactory.session()` |
| 외부 세션 사용 | `args[0]` 타입 체크 (암묵적) | `session=session` 전달 (명시적) |

---

## 8. Step 7: 개별 Repository 구현

archive의 기존 Repository를 참조하여 특수 메서드를 새 패턴으로 재작성합니다.

### 8.1 PulseliveRepository

**파일**: `repository/repositories/pulselive.py`

```python
from typing import TypeVar

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.repository.entities.base import PulseliveEntity
from football_data_manager.repository.repositories.base import AsyncBaseRepository

TEntity = TypeVar("TEntity", bound=PulseliveEntity)


class PulseliveRepository(AsyncBaseRepository[TEntity]):
    """Repository for Pulselive-sourced entities."""

    async def exists_by_pulselive_id(self, source_id: str) -> bool:
        """Check existence by Pulselive source ID."""
        return await self.exists_by_source(SourceEnum.PULSELIVE, source_id)

    async def get_by_pulselive_id(self, source_id: str) -> TEntity | None:
        """Get entity by Pulselive source ID."""
        return await self.get_by_source(SourceEnum.PULSELIVE, source_id)
```

### 8.2 개별 Repository 목록 및 특수 메서드

각 Repository는 해당 Entity에 특화된 메서드를 포함합니다. archive 참조:

| Repository | 상속 | 특수 메서드 (archive 참조) |
|------------|------|--------------------------|
| `AnalyticsRepository` | `AsyncBaseRepository` | `upsert()`, `get_by_season_and_key()` |
| `AwardRepository` | `PulseliveRepository` | `get_by_name_en()` |
| `CompetitionRepository` | `PulseliveRepository` | (없음) |
| `FixtureRepository` | `PulseliveRepository` | (없음) |
| `GroundRepository` | `PulseliveRepository` | (없음) |
| `MatchRepository` | `PulseliveRepository` | `load_items()`, `get_by_fixture()`, `get_by_team_on_season()`, `get_by_season()`, `append_card()`, `append_goal()`, `append_lineup()`, `append_substitute()`, `append_substitution()` |
| `MatchStatRepository` | `PulseliveRepository` | (없음) |
| `NewsRepository` | `AsyncBaseRepository` | (없음) |
| `OfficialRepository` | `PulseliveRepository` | (없음) |
| `PlayerRepository` | `PulseliveRepository` | `load_championship_seasons()`, `get_nationality_kr()`, `append_championship_season()`, `get_by_display_name_en()`, `get_by_full_name()`, `get_by_ids()` |
| `PlayerStatRepository` | `PulseliveRepository` | (없음) |
| `SeasonRepository` | `PulseliveRepository` | (없음) |
| `StaffRepository` | `PulseliveRepository` | (없음) |
| `TeamRepository` | `PulseliveRepository` | `load_championship_seasons()`, `append_championship_season()`, `get_by_abbr()`, `get_by_name_en()` |
| `TeamStatRepository` | `PulseliveRepository` | `load_matches()`, `append_match()`, `get_by_season_and_team()` |

### 8.3 구현 예시: PlayerRepository

**파일**: `repository/repositories/players.py`

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.repository.entities.players import (
    PlayerEntity,
    PlayerChampionshipAssociation,
)
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class PlayerRepository(PulseliveRepository[PlayerEntity]):
    """Repository for player entities with championship management."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, PlayerEntity)

    async def load_championship_seasons(
        self, player: PlayerEntity
    ) -> PlayerEntity:
        """Load championship season associations for the player."""
        return await self._load_lazy_fields(
            player,
            [PlayerChampionshipAssociation.SEASON_COLLECTION_NAME],
        )

    async def get_nationality_kr(self, nationality_en: str) -> str | None:
        """Get Korean nationality name by English name."""
        result = await self._get_one_by_field(nationality_en=nationality_en)
        return result.nationality_kr if result else None

    async def append_championship_season(
        self, player: PlayerEntity, season: SeasonEntity
    ) -> PlayerEntity:
        """Append a championship season if not already associated."""
        merged = await self.load_championship_seasons(player)
        existing_ids = {
            a.season_id for a in merged.championship_season_associations
        }
        if season.id not in existing_ids:
            assoc = PlayerChampionshipAssociation(
                player=merged, season=season, date_end=season.date_end
            )
            merged.championship_season_associations.append(assoc)
        merged.championship_season_associations.sort(key=lambda s: s.date_end)
        return merged

    async def get_by_display_name_en(self, name: str) -> PlayerEntity | None:
        """Get player by English display name."""
        return await self._get_one_by_field(display_name_en=name)

    async def get_by_full_name(self, name: str) -> PlayerEntity | None:
        """Get player by full legal name."""
        return await self._get_one_by_field(full_name=name)

    async def get_by_ids(self, ids: list[str]) -> list[PlayerEntity]:
        """Get multiple players by IDs."""
        if not ids:
            return []
        async with self._session_factory.session() as s:
            stmt = select(PlayerEntity).where(PlayerEntity.id.in_(ids))
            result = await s.execute(stmt)
            return list(result.scalars().all())
```

### 8.4 메서드 이름 변경 매핑

기존 Repository 메서드와 새 Repository 메서드의 대응:

| 기존 메서드 | 새 메서드 | 이유 |
|------------|----------|------|
| `read_all()` | `get_all()` | 일관된 `get_` prefix |
| `read_by_id()` | `get_by_id()` | 일관된 `get_` prefix |
| `read_by_source_id()` | `get_by_source()` | 간결화 |
| `read_by_pulselive_id()` | `get_by_pulselive_id()` | 일관된 `get_` prefix |
| `_read_by_field()` | `_get_by_field()` | 일관된 `get_` prefix |
| `_read_one_by_field()` | `_get_one_by_field()` | 일관된 `get_` prefix |
| `create_all()` | `create_many()` | Master plan 네이밍 준수 |

---

## 9. Step 8: RepositoryContainer 구현

dependency-injector를 사용한 DI 컨테이너입니다.

### 9.1 구현

**파일**: `repository/container.py`

```python
from dependency_injector import containers, providers

from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.repository.session import SessionFactory
from football_data_manager.repository.repositories.analytics import AnalyticsRepository
from football_data_manager.repository.repositories.awards import AwardRepository
from football_data_manager.repository.repositories.competitions import CompetitionRepository
from football_data_manager.repository.repositories.fixtures import FixtureRepository
from football_data_manager.repository.repositories.grounds import GroundRepository
from football_data_manager.repository.repositories.match_stats import MatchStatRepository
from football_data_manager.repository.repositories.matches import MatchRepository
from football_data_manager.repository.repositories.news import NewsRepository
from football_data_manager.repository.repositories.officials import OfficialRepository
from football_data_manager.repository.repositories.player_stats import PlayerStatRepository
from football_data_manager.repository.repositories.players import PlayerRepository
from football_data_manager.repository.repositories.seasons import SeasonRepository
from football_data_manager.repository.repositories.staffs import StaffRepository
from football_data_manager.repository.repositories.team_stats import TeamStatRepository
from football_data_manager.repository.repositories.teams import TeamRepository


class RepositoryContainer(containers.DeclarativeContainer):
    """DI container for all repositories."""

    config_service = providers.Dependency(instance_of=ConfigService)

    session_factory = providers.Singleton(
        SessionFactory,
        config_service=config_service,
    )

    analytics_repository = providers.Singleton(
        AnalyticsRepository, session_factory=session_factory
    )
    award_repository = providers.Singleton(
        AwardRepository, session_factory=session_factory
    )
    competition_repository = providers.Singleton(
        CompetitionRepository, session_factory=session_factory
    )
    fixture_repository = providers.Singleton(
        FixtureRepository, session_factory=session_factory
    )
    ground_repository = providers.Singleton(
        GroundRepository, session_factory=session_factory
    )
    match_stat_repository = providers.Singleton(
        MatchStatRepository, session_factory=session_factory
    )
    match_repository = providers.Singleton(
        MatchRepository, session_factory=session_factory
    )
    news_repository = providers.Singleton(
        NewsRepository, session_factory=session_factory
    )
    official_repository = providers.Singleton(
        OfficialRepository, session_factory=session_factory
    )
    player_stat_repository = providers.Singleton(
        PlayerStatRepository, session_factory=session_factory
    )
    player_repository = providers.Singleton(
        PlayerRepository, session_factory=session_factory
    )
    season_repository = providers.Singleton(
        SeasonRepository, session_factory=session_factory
    )
    staff_repository = providers.Singleton(
        StaffRepository, session_factory=session_factory
    )
    team_stat_repository = providers.Singleton(
        TeamStatRepository, session_factory=session_factory
    )
    team_repository = providers.Singleton(
        TeamRepository, session_factory=session_factory
    )
```

### 9.2 기존 대비 변경 사항

| 항목 | 기존 | 새로운 |
|------|------|--------|
| 세션 주입 | `db_service=db_service` | `session_factory=session_factory` |
| TeamStatRepository | `match_repository` 추가 주입 | 동일 (필요 시) |
| Repository 수 | 14개 (Analytics 미포함) | 15개 (Analytics 포함) |

---

## 10. Step 9: Alembic 재설정

Entity 경로가 변경되었으므로 `env.py`의 import를 업데이트합니다.

### 10.1 `env.py` import 변경

```python
# 변경 전 (common/repositories/ 경로)
from football_data_manager.common.repositories import Base
from football_data_manager.common.repositories.analytics.analytics_entity import AnalyticsEntity
...

# 변경 후 (repository/entities/ 경로)
from football_data_manager.repository.entities.base import Base
from football_data_manager.repository.entities.analytics import AnalyticsEntity
from football_data_manager.repository.entities.awards import AwardEntity
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.entities.match_stats import MatchStatEntity
from football_data_manager.repository.entities.matches import (
    MatchEntity,
    MatchCardAssociation,
    MatchGoalAssociation,
    MatchLineupAssociation,
    MatchSubstituteAssociation,
    MatchSubstitutionAssociation,
)
from football_data_manager.repository.entities.news import (
    NewsEntity,
    NewsTeamAssociation,
)
from football_data_manager.repository.entities.officials import OfficialEntity
from football_data_manager.repository.entities.player_stats import (
    PlayerStatEntity,
    PlayerStatAwardAssociation,
)
from football_data_manager.repository.entities.players import (
    PlayerEntity,
    PlayerChampionshipAssociation,
)
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.staffs import (
    StaffEntity,
    StaffAwardAssociation,
)
from football_data_manager.repository.entities.team_stats import (
    TeamStatEntity,
    TeamStatMatchAssociation,
)
from football_data_manager.repository.entities.teams import (
    TeamEntity,
    TeamChampionshipAssociation,
)
```

### 10.2 마이그레이션 생성 (Entity 변경 확인)

```bash
# Entity 이동 후 차이가 있는지 확인
alembic revision --autogenerate -m "Verify entity migration"

# 생성된 파일에 실제 변경이 없어야 함 (테이블 구조 동일)
# 만약 변경이 있다면 Entity 변환 과정에서 실수가 있는 것
```

---

## 11. Step 10: 검증

### 11.1 Python import 검증

```bash
python -c "
from football_data_manager.repository.entities.base import Base, BaseEntity, PulseliveEntity
print(f'Tables registered: {len(Base.metadata.tables)}')
for name in sorted(Base.metadata.tables.keys()):
    print(f'  - {name}')
"
```

기대 결과: 26개 테이블 출력

### 11.2 Repository import 검증

```bash
python -c "
from football_data_manager.repository.repositories.players import PlayerRepository
from football_data_manager.repository.repositories.matches import MatchRepository
from football_data_manager.repository.repositories.teams import TeamRepository
print('All repository imports successful')
"
```

### 11.3 Container 검증

```bash
python -c "
from football_data_manager.repository.container import RepositoryContainer
print(f'Container providers: {len(RepositoryContainer.providers)}')
"
```

### 11.4 Alembic 검증

```bash
# env.py 새 import로 로딩 확인
python -c "
from alembic.config import Config
config = Config('alembic.ini')
print('Alembic config loaded successfully')
"
```

---

## 12. 검증 체크리스트

### 12.1 Entity 마이그레이션

- [x] `repository/entities/base.py` 생성 (Base, BaseEntity, PulseliveEntity) ✅ Step 3
- [x] 15개 Entity 파일 생성 (`repository/entities/*.py`) ✅ Step 4
- [x] 11개 Association이 해당 Entity 파일에 포함 ✅ Step 4
- [x] 모든 Entity가 `Mapped[T]` + `mapped_column()` 사용 ✅ Step 4
- [x] 26개 테이블 등록 확인 ✅ Step 4 (import 검증 완료)
- [x] `__init__` 메서드 로직 보존 확인 ✅ Step 4
- [x] `constants.py` 상수가 각 Entity 파일로 이동 ✅ Step 4

### 12.2 Repository 구현

- [x] `repository/session.py` 생성 (SessionFactory) ✅ Step 5
- [x] `repository/repositories/base.py` 생성 (AsyncBaseRepository) ✅ Step 6
- [x] `repository/repositories/pulselive.py` 생성 (PulseliveRepository) ✅ Step 7
- [x] 15개 개별 Repository 생성 ✅ Step 7
- [x] 특수 메서드 구현 (archive 참조, 8.2 테이블 참고) ✅ Step 7
- [x] `repository/container.py` 생성 (RepositoryContainer) ✅ Step 8

### 12.3 Alembic 업데이트

- [x] `env.py` import 경로 업데이트 ✅ Step 9
- [ ] `alembic revision --autogenerate`로 불필요한 변경 없음 확인 (DB 연결 필요)

### 12.4 정리

- [ ] `common/repositories/` 디렉토리 제거 (또는 archive) — Phase 2에서 처리
- [ ] `common/services/db/` 빈 디렉토리 제거 — Phase 2에서 처리

---

## 13. Phase 1 완료 기준

다음 조건을 **모두** 만족해야 Phase 2로 진행 가능:

1. **Entity**: 15개 Entity + 11개 Association이 `repository/entities/`에 존재
2. **Repository**: 15개 Repository + Base + Pulselive가 `repository/repositories/`에 존재
3. **Session**: `SessionFactory`가 정상 동작 (ConfigService 연동)
4. **Container**: `RepositoryContainer`가 15개 Repository를 모두 제공
5. **Alembic**: 새 Entity 경로에서 26개 테이블 인식, 불필요한 마이그레이션 없음
6. **Import**: 모든 새 경로 import 성공

---

## 14. 다음 단계

Phase 1 완료 후:

1. **Phase 2 계획 문서 읽기**: (작성 예정)
2. **Puller 리팩토링 시작**: Interface 구조 생성, AbstractPuller 구현
3. **Puller에서 새 Repository 사용**: import 경로를 `football_data_manager.repository.repositories.*`로 변경

---

## Appendix A: archive 참조 파일 경로

Phase 1 구현 시 참조할 archive 파일 목록:

| 참조 용도 | archive 경로 |
|----------|-------------|
| BaseRepository 패턴 | `archive/football_data_manager/common/repositories/base_repository.py` |
| PulseliveRepository | `archive/football_data_manager/common/repositories/pulselive_repository.py` |
| DbService (Session 참조) | `archive/football_data_manager/common/services/db/db_service.py` |
| RepositoryContainer | `archive/football_data_manager/common/repositories/repository_container.py` |
| PlayerRepository | `archive/football_data_manager/common/repositories/players/player_repository.py` |
| MatchRepository | `archive/football_data_manager/common/repositories/matches/match_repository.py` |
| TeamRepository | `archive/football_data_manager/common/repositories/teams/team_repository.py` |
| TeamStatRepository | `archive/football_data_manager/common/repositories/team_stats/team_stat_repository.py` |
| AnalyticsRepository | `archive/football_data_manager/common/repositories/analytics/analytics_repository.py` |

---

## Appendix B: 트러블슈팅

### B.1 `DeclarativeBase` import 오류

**원인**: SQLAlchemy 버전이 2.0 미만

```bash
pip install --upgrade sqlalchemy
python -c "import sqlalchemy; print(sqlalchemy.__version__)"
# 2.0+ 이어야 함
```

### B.2 `Mapped` 타입과 nullable 불일치

**문제**: `Mapped[str]`인데 `nullable=True` → 타입 불일치 경고

**해결**: nullable 컬럼은 `Mapped[str | None]` 사용

```python
# 올바른 사용
name: Mapped[str] = mapped_column(String, nullable=False)       # 필수
photo: Mapped[str | None] = mapped_column(String, nullable=True)  # 선택
```

### B.3 Association 테이블 순환 import

**문제**: Entity A가 Entity B를 FK로 참조하고, Association이 양쪽을 참조

**해결**: FK는 문자열로 테이블명 참조

```python
# 순환 import 방지: Entity 클래스 대신 테이블명 문자열 사용
player_id: Mapped[str] = mapped_column(
    ForeignKey("players.id", ondelete="CASCADE"),
    nullable=False,
)
```

### B.4 Alembic autogenerate에서 불필요한 diff 발생

**원인**: `Mapped[T]` 변환 시 타입 매핑이 기존과 미세하게 다름

**해결**: 생성된 마이그레이션 파일을 수동으로 검토하고, 실제 스키마 변경이 없는 diff는 제거

---

**Document End**
