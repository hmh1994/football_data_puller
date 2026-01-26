# Football Data Puller - Refactoring Master Plan

## 1. Executive Summary

이 문서는 Football Data Puller 프로젝트의 전체 리팩토링 계획을 담고 있습니다. 프로젝트를 네 가지 핵심 컴포넌트로 재구성합니다:

1. **Repository**: PostgreSQL + SQLAlchemy 기반 비동기 ORM 서비스
2. **Puller**: 다중 데이터 소스를 위한 확장 가능한 데이터 수집 서비스
3. **Merger**: 데이터 병합 및 연산 모듈
4. **Scheduler**: 크론 기반 자동화 스케줄러

### 관련 문서

- **상세 현황 분석**: `current_state_analysis.md` - 현재 코드베이스의 상세 구조 (15 entities, 11 associations, 20 pullers)
- **Phase 0 가이드**: `phase_0_preparation.md` - Alembic 설정 실행 가이드 (ConfigService 연동)
- **문서 개요**: `README.md` - 문서 읽기 순서 및 FAQ

---

## 2. Current State Analysis (현재 상태 분석)

### 2.1 프로젝트 구조

```
football_data_manager/
├── common/
│   ├── enums/                    # 8개 Enum 정의
│   ├── repositories/             # 15개 테이블 (Entity + Repository)
│   │   ├── base_entity.py        # BaseEntity (id, source, source_id, timestamps)
│   │   ├── base_repository.py    # BaseRepository (Generic CRUD)
│   │   ├── pulselive_entity.py   # PulseliveEntity extends BaseEntity
│   │   ├── repository_container.py
│   │   ├── awards/
│   │   ├── competitions/
│   │   ├── fixtures/
│   │   ├── grounds/
│   │   ├── matches/              # + 5개 Association 테이블
│   │   ├── match_stats/
│   │   ├── news/                 # + 1개 Association 테이블
│   │   ├── officials/
│   │   ├── player_stats/         # + 1개 Association 테이블
│   │   ├── players/              # + 1개 Association 테이블
│   │   ├── seasons/
│   │   ├── staffs/               # + 1개 Association 테이블
│   │   ├── team_stats/           # + 1개 Association 테이블
│   │   ├── teams/                # + 1개 Association 테이블
│   │   └── analytics/
│   ├── services/
│   │   ├── config/
│   │   ├── db/                   # DbService (AsyncEngine + Session)
│   │   ├── client/               # HTTP, GraphQL, OpenAI, Anthropic clients
│   │   └── translator/
│   └── utils/
└── puller/
    └── services/
        ├── pulselive_new/        # 주력 데이터 소스 (v2/v3 API)
        │   ├── models/responses/ # ~50개 Pydantic 모델
        │   ├── components/       # WebClient
        │   └── services/         # 10개 Puller 서비스
        ├── pulselive/            # 레거시 데이터 소스
        └── the_athletic/         # 뉴스 데이터 소스
```

### 2.2 기존 테이블 목록 (유지 예정)

| Table        | Entity            | Association Tables                           |
|--------------|-------------------|----------------------------------------------|
| awards       | AwardEntity       | -                                            |
| competitions | CompetitionEntity | -                                            |
| fixtures     | FixtureEntity     | -                                            |
| grounds      | GroundEntity      | -                                            |
| matches      | MatchEntity       | card, goal, lineup, substitute, substitution |
| match_stats  | MatchStatEntity   | -                                            |
| news         | NewsEntity        | team                                         |
| officials    | OfficialEntity    | -                                            |
| player_stats | PlayerStatEntity  | award                                        |
| players      | PlayerEntity      | championship                                 |
| seasons      | SeasonEntity      | -                                            |
| staffs       | StaffEntity       | award                                        |
| team_stats   | TeamStatEntity    | match                                        |
| teams        | TeamEntity        | championship                                 |
| analytics    | AnalyticsEntity   | -                                            |

### 2.3 현재 기술 스택

- **Python**: 3.12+
- **ORM**: SQLAlchemy 2.x (Async)
- **Validation**: Pydantic 2.x
- **DI**: dependency-injector
- **HTTP**: httpx (async)

---

## 3. Target Architecture (목표 아키텍처)

### 3.1 새로운 디렉토리 구조

```
football_data_manager/
├── repository/                   # Component 1: Repository
│   ├── entities/                 # SQLAlchemy Entity 정의
│   │   ├── base.py              # Base, BaseEntity
│   │   ├── players.py           # PlayerEntity, PlayerChampionshipAssociation
│   │   ├── teams.py
│   │   ├── ... (테이블별 파일)
│   │   └── __init__.py
│   ├── repositories/            # Repository 클래스
│   │   ├── base.py              # AsyncBaseRepository
│   │   ├── players.py
│   │   ├── ...
│   │   └── __init__.py
│   ├── migrations/              # Alembic 마이그레이션
│   │   ├── versions/
│   │   ├── env.py
│   │   └── alembic.ini
│   ├── session.py               # AsyncSession Factory
│   └── container.py             # RepositoryContainer
│
├── puller/                       # Component 2: Puller
│   ├── interfaces/              # Pydantic 인터페이스 (TypedDict + BaseModel)
│   │   ├── pulselive/
│   │   │   ├── player.py        # TypedDict 기반 내부 모델
│   │   │   └── ...
│   │   ├── the_athletic/
│   │   └── __init__.py
│   ├── clients/                 # HTTP 클라이언트
│   │   ├── base.py              # AsyncBaseClient
│   │   ├── pulselive.py
│   │   ├── the_athletic.py
│   │   └── __init__.py
│   ├── pullers/                 # Puller 구현체
│   │   ├── base.py              # AbstractPuller
│   │   ├── pulselive/
│   │   │   ├── player.py
│   │   │   ├── team.py
│   │   │   └── ...
│   │   └── the_athletic/
│   └── container.py             # PullerContainer
│
├── merger/                       # Component 3: Merger
│   ├── base.py                  # AbstractMerger
│   ├── players/                 # Table별 Merger
│   │   ├── player_merger.py
│   │   └── player_stat_merger.py
│   ├── teams/
│   ├── matches/
│   ├── ...
│   └── container.py             # MergerContainer
│
├── scheduler/                    # Component 4: Scheduler
│   ├── jobs/                    # Job 정의
│   │   ├── base.py              # AbstractJob
│   │   ├── player_sync.py
│   │   ├── match_update.py
│   │   └── ...
│   ├── config.py                # 스케줄 설정
│   ├── runner.py                # 스케줄러 실행기
│   └── container.py             # SchedulerContainer
│
└── common/                       # 공유 유틸리티
    ├── enums/
    ├── config/
    ├── utils/
    └── clients/                 # 외부 서비스 (OpenAI, Anthropic, Translator)
```

---

## 4. Component Design (컴포넌트 설계)

### 4.1 Repository Component

#### 4.1.1 Migration 도구 선택

**[DECISION]: Migration 도구 선택**
✅ **Alembic 선택**

이유:
- SQLAlchemy 공식 마이그레이션 도구
- Async 완벽 지원 (SQLAlchemy 2.x)
- Auto-generate 기능 (`alembic revision --autogenerate`)
- 가장 성숙하고 안정적
- Django migrations와 유사한 워크플로우

#### 4.1.2 AsyncBaseRepository 설계

```python
from typing import TypeVar, Generic, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

TEntity = TypeVar("TEntity", bound="BaseEntity")


class AsyncBaseRepository(Generic[TEntity]):
    """간결한 비동기 Repository 베이스 클래스"""

    def __init__(self, session_factory: AsyncSessionFactory, model: type[TEntity]):
        self._session_factory = session_factory
        self._model = model

    # Create
    async def create(self, entity: TEntity) -> TEntity: ...

    async def create_many(self, entities: Sequence[TEntity]) -> list[TEntity]: ...

    # Read
    async def get_by_id(self, entity_id: str) -> TEntity | None: ...

    async def get_by_source(self, source: SourceEnum, source_id: str) -> TEntity | None: ...

    async def get_all(self, *, limit: int | None = None, offset: int = 0) -> list[TEntity]: ...

    async def count(self, *filters) -> int: ...

    async def exists(self, entity_id: str) -> bool: ...

    # Update
    async def update(self, entity: TEntity) -> TEntity: ...

    async def upsert(self, entity: TEntity) -> TEntity: ...

    # Delete
    async def delete(self, entity: TEntity) -> None: ...

    async def delete_by_id(self, entity_id: str) -> bool: ...
```

#### 4.1.3 Entity 변경사항

현재 Entity 구조는 유지하되, 다음 개선사항을 적용합니다:

- `declarative_base` → SQLAlchemy 2.0 스타일 `DeclarativeBase` 사용
- 타입 힌트 강화 (`Mapped[T]` 사용)
- Association 테이블은 동일 파일 내 정의

**[DECISION]: Entity 구조 변경 범위**
✅ **기존 패턴 (`source`/`source_id`) 유지**

이유:
- 멀티소스 지원 용이 (현재 PULSELIVE, THE_ATHLETIC 사용 중)
- 향후 확장성 (새 소스 추가 시 스키마 변경 불필요)
- `(source, source_id)` 복합 unique 인덱스 효율적

### 4.2 Puller Component

#### 4.2.1 Interface 설계 원칙

1. **외부 API 응답 그대로 보존** - 데이터 변조 없음
2. **snake_case 변환만 허용** - Python 컨벤션 적용
3. **성능 최적화**:
    - Top-level 모델: `BaseModel` (검증 필요)
    - Nested 모델: `TypedDict` (빠른 파싱)

```python
# interfaces/pulselive/player.py
from typing import TypedDict
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PlayerCountryDict(TypedDict):
    country: str
    iso_code: str | None


class PlayerNameDict(TypedDict):
    simple_name: str
    full_name: str


class PlayerResponse(BaseModel):
    """Top-level response - uses BaseModel for validation"""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: str
    name: PlayerNameDict  # TypedDict for nested
    country: PlayerCountryDict
    position: str
    height: int | None = None
    weight: int | None = None
```

#### 4.2.2 Puller 구조

```python
# pullers/base.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

TResponse = TypeVar("TResponse", bound=BaseModel)


class AbstractPuller(ABC, Generic[TResponse]):
    """모든 Puller의 추상 베이스 클래스"""

    @abstractmethod
    async def pull(self, **kwargs) -> TResponse | list[TResponse]:
        """데이터를 가져와 Pydantic 모델로 반환"""
        ...

    @abstractmethod
    async def close(self) -> None:
        """리소스 정리"""
        ...
```

**[DECISION]: 새로운 데이터 소스 계획**
✅ **현재는 추가 계획 없음**

현재 데이터 소스:
- `pulselive_new` (주력)
- `pulselive` (레거시, 참고용 유지)
- `the_athletic` (뉴스)

향후 고려 가능 소스:
- FBRef (상세 통계)
- Transfermarkt (이적 시장)
- Understat (xG 등 고급 통계)

### 4.3 Merger Component

#### 4.3.1 Merger 설계

**설계 원칙**:
- ❌ **추상 클래스 사용 안 함** (각 Merger가 고유 로직을 가짐)
- ✅ **구체적 Merger만 구현** (필요한 메서드만 정의)
- ✅ **멀티 소스 지원** (하나의 Merger가 여러 Response 타입 처리)

```python
# merger/players/player_merger.py
class PlayerMerger:
    """선수 데이터 병합 - 여러 API 응답 처리 가능"""
    
    def __init__(
        self,
        player_repository: PlayerRepository,
        translator_service: TranslatorService
    ):
        self._repository = player_repository
        self._translator = translator_service
    
    async def merge_from_pulselive(
        self, 
        response: PulselivePlayerResponse
    ) -> PlayerEntity:
        """Pulselive v2/squad API 응답으로부터 병합"""
        existing = await self._repository.read_by_pulselive_id(response.id)
        
        if existing:
            return await self._update_existing(existing, response)
        else:
            return await self._create_new(response)
    
    async def merge_from_detail(
        self, 
        response: PlayerDetailResponse
    ) -> PlayerEntity:
        """Pulselive v1/player-detail API 응답으로부터 병합 (다른 구조)"""
        # 다른 응답 구조 처리
        ...
    
    async def _create_new(self, response: PulselivePlayerResponse) -> PlayerEntity:
        """새 선수 Entity 생성"""
        entity = PlayerEntity(
            source_id=response.id,
            display_name_en=response.name.simple_name,
            display_name_kr=await self._translator.translate(response.name.simple_name),
            # ... 필드 매핑
        )
        return await self._repository.create(entity)
    
    async def _update_existing(
        self, 
        existing: PlayerEntity, 
        response: PulselivePlayerResponse
    ) -> PlayerEntity:
        """기존 선수 정보 업데이트 (변경된 필드만)"""
        changed = False
        
        if existing.position != response.position:
            existing.position = response.position
            changed = True
        
        if existing.height != response.height:
            existing.height = response.height
            changed = True
        
        if changed:
            return await self._repository.update(existing)
        else:
            return existing
```

#### 4.3.2 Table별 Merger 매핑

| Table        | Merger            | 설명             |
|--------------|-------------------|----------------|
| players      | PlayerMerger      | 선수 기본 정보 생성/갱신 |
| player_stats | PlayerStatMerger  | 시즌별 통계 생성/갱신   |
| teams        | TeamMerger        | 팀 정보 생성/갱신     |
| team_stats   | TeamStatMerger    | 팀 시즌 통계 생성/갱신  |
| matches      | MatchMerger       | 경기 결과 생성/갱신    |
| fixtures     | FixtureMerger     | 경기 일정 생성/갱신    |
| seasons      | SeasonMerger      | 시즌 정보 생성       |
| competitions | CompetitionMerger | 대회 정보 생성       |
| news         | NewsMerger        | 뉴스 생성          |
| ...          | ...               | ...            |

**[DECISION]: Merger 설계 방향**
✅ **구조부터 잡고 점진적 구현**
✅ **Abstraction 없이 구체적 Merger만 구현**

이유:
- 각 Merger는 고유한 로직을 가짐 (공통 패턴 없음)
- 하나의 Merger가 여러 Puller Response를 처리할 수 있음
- 강제된 abstraction이 오히려 복잡도 증가

**수정된 설계**:
```python
# merger/players/player_merger.py
class PlayerMerger:
    """구체적 Merger - 추상 클래스 상속 없음"""
    
    def __init__(self, player_repository: PlayerRepository):
        self._repository = player_repository
    
    async def merge_from_pulselive(self, response: PulselivePlayerResponse) -> PlayerEntity:
        """Pulselive API 응답으로부터 병합"""
        ...
    
    async def merge_from_squad(self, response: SquadPlayerResponse) -> PlayerEntity:
        """Squad API 응답으로부터 병합 (다른 구조)"""
        ...
```

**우선순위**: Phase 3에서 필요한 것부터 점진적 구현

### 4.4 Scheduler Component

#### 4.4.1 스케줄 설정

```python
# scheduler/config.py
from dataclasses import dataclass
from enum import Enum


class Interval(Enum):
    FIVE_MINUTES = "*/5 * * * *"
    TEN_MINUTES = "*/10 * * * *"
    HOURLY = "0 * * * *"
    DAILY = "0 0 * * *"
    MONTHLY = "0 0 1 * *"


@dataclass
class JobConfig:
    name: str
    interval: Interval
    job_callable: Callable  # Merger 직접 호출
    enabled: bool = True
```

#### 4.4.2 Job-Merger 매핑 (예시)

| Interval | Jobs             | Target Tables            |
|----------|------------------|--------------------------|
| 5분       | LiveMatchJob     | matches, match_stats     |
| 10분      | FixtureUpdateJob | fixtures                 |
| 1시간      | PlayerStatsJob   | player_stats, team_stats |
| 1일       | PlayerSyncJob    | players, teams           |
| 1달       | SeasonSetupJob   | seasons, competitions    |

**[DECISION]: 스케줄러 라이브러리 선택**
✅ **APScheduler 선택**

이유:
- Async 지원 (`AsyncIOScheduler`)
- 가장 성숙하고 안정적 (10년+ 프로덕션 사용)
- Cron, Interval, Date 트리거 모두 지원
- 단순한 단일 서버 환경에 적합
- 에러 핸들링 및 모니터링 내장

---

## 5. Migration Strategy (마이그레이션 전략)

### 5.1 단계별 마이그레이션

#### Phase 0: Preparation (2-3일)

**선행 조건**: `4_combined_migration_plan.md` 실행 완료 (app.py 구현, 레거시 정리)

1. Alembic 설치 및 초기화
2. `alembic.ini` 설정
3. `env.py` 설정 (ConfigService에서 DB 설정 읽어오기)
4. 설정 검증

**완료 기준**: Alembic이 ConfigService에서 DB 설정을 성공적으로 읽어올 수 있음

> ℹ️ **마이그레이션 생성/적용은 Phase 1 이후 각 단계에서 수행**

#### Phase 1: Repository 리팩토링 (1-2주)

1. 초기 마이그레이션 생성 및 적용
2. 새로운 디렉토리 구조 생성
3. Entity 클래스 마이그레이션 (구조 유지)
4. AsyncBaseRepository 구현
5. 기존 테스트 마이그레이션 및 검증

#### Phase 2: Puller 리팩토링 (1-2주)

1. Interface 디렉토리 구조 생성
2. TypedDict 기반 내부 모델 정의
3. BaseModel top-level 응답 모델 정의
4. AbstractPuller 및 개별 Puller 구현
5. 기존 Puller 기능 검증

#### Phase 3: Merger 구현 (1-2주)

1. Merger 디렉토리 구조 생성
2. 필요한 Merger부터 점진적 구현 (추상화 없이)
3. 각 Merger별 단위 테스트 작성
4. 통합 테스트 검증

**참고**: Abstraction 없이 각 테이블별 구체적 Merger 구현

#### Phase 4: Scheduler 구현 (1주)

1. 스케줄러 라이브러리 설정
2. Job 클래스 구현
3. Merger 연동
4. 전체 통합 테스트

### 5.2 병렬 작업 가능 영역

```
Phase 1 ─────────────────────────────────►
         └─ Phase 2 ─────────────────────►
                     └─ Phase 3 ─────────►
                                 └─ Phase 4 ─►
```

Phase 2는 Phase 1 중간부터, Phase 3는 Phase 2 중간부터 시작 가능합니다.

---

## 6. Technical Decisions (기술적 결정 사항)

### 6.1 확정된 결정

| 항목         | 결정                  | 이유               |
|------------|---------------------|------------------|
| ORM        | SQLAlchemy 2.x      | 기존 코드 호환, 비동기 지원 |
| Validation | Pydantic 2.x        | 기존 사용 중, 성능 우수   |
| DI         | dependency-injector | 기존 사용 중          |
| HTTP       | httpx               | 비동기 지원, 기존 사용 중  |
| Database   | PostgreSQL          | 기존 사용 중          |

### 6.2 결정 필요 사항

**[모든 결정 완료]**

1. ✅ **Migration 도구**: Alembic
2. ✅ **Scheduler 라이브러리**: APScheduler
3. ✅ **Merger 설계**: Abstraction 없이 구체적 구현 (점진적 접근)
4. ✅ **추가 데이터 소스**: 현재 계획 없음
5. ✅ **Entity source/source_id 패턴**: 유지

---

## 7. Risk Assessment (리스크 평가)

### 7.1 기술적 리스크

| 리스크        | 확률 | 영향 | 완화 전략                |
|------------|----|----|----------------------|
| 기존 데이터 손실  | 낮음 | 높음 | 마이그레이션 전 백업, 단계별 검증  |
| API 호환성 문제 | 중간 | 중간 | Interface 테스트 케이스 확보 |
| 성능 저하      | 낮음 | 중간 | 벤치마크 테스트 추가          |

### 7.2 일정 리스크

| 리스크          | 확률 | 영향 | 완화 전략               |
|--------------|----|----|---------------------|
| 예상보다 긴 개발 기간 | 중간 | 중간 | 병렬 작업, MVP 우선 접근    |
| 테스트 커버리지 부족  | 중간 | 높음 | 각 Phase 완료 전 테스트 필수 |

---

## 8. Success Criteria (성공 기준)

### 8.1 기능적 기준

- [ ] 모든 기존 Entity 구조 유지
- [ ] 모든 기존 테스트 통과
- [ ] 새로운 비동기 Repository 동작 검증
- [ ] Puller → Merger → Repository 파이프라인 동작
- [ ] Scheduler 자동 실행 검증

### 8.2 비기능적 기준

- [ ] 응답 시간: 기존 대비 동등 또는 개선
- [ ] 코드 복잡도: 간결성 향상
- [ ] 테스트 커버리지: 80% 이상
- [ ] 문서화: 각 컴포넌트 README 작성

---

## 9. Next Steps (다음 단계)

1. **이 문서의 [NEED_YOUR_COMMENT] 항목에 대한 피드백 제공**
2. 피드백 반영 후 상세 구현 계획 수립
3. Phase 1 시작

---

## Appendix A: 기존 파일 매핑

### Repository 파일 (이동 예정)

| 현재 경로                                              | 새 경로                                 |
|----------------------------------------------------|--------------------------------------|
| `common/repositories/base_entity.py`               | `repository/entities/base.py`        |
| `common/repositories/base_repository.py`           | `repository/repositories/base.py`    |
| `common/repositories/players/player_entity.py`     | `repository/entities/players.py`     |
| `common/repositories/players/player_repository.py` | `repository/repositories/players.py` |
| ...                                                | ...                                  |

### Puller 파일 (이동 예정)

| 현재 경로                                             | 새 경로                           |
|---------------------------------------------------|--------------------------------|
| `puller/services/pulselive_new/models/responses/` | `puller/interfaces/pulselive/` |
| `puller/services/pulselive_new/services/`         | `puller/pullers/pulselive/`    |
| `puller/services/the_athletic/`                   | `puller/pullers/the_athletic/` |

---

*문서 생성일: 2026-01-13*
*마지막 수정: 2026-01-26*

---

## 변경 이력

### 2026-01-26
- 모든 [NEED_YOUR_COMMENT] 항목 결정 완료
- Merger 설계: Abstraction 제거, 구체적 구현으로 변경
- 모든 기술 스택 결정 확정 (Alembic, APScheduler)
- source/source_id 패턴 유지 결정
