# Phase 4: Data Syncer 구현

**상태**: 진행 중 🚧 (핵심 구현 및 단위 검증 완료, 통합 검증 대기)
**목표**: `app.py`에 데이터 동기화 명령어 추가 (입력 파라미터 기반 선택적 Pull → Merge → DB 갱신)
**선행 조건**: Phase 3 완료 ✅

> **시작 전에**: 이 문서는 실행 가이드입니다. 전체 계획은 `1_master_plan.md`를 참고하세요.

---

## 목차

1. [개요](#1-개요)
2. [Step 1: 데이터 종속성 그래프 설계](#2-step-1-데이터-종속성-그래프-설계)
3. [Step 2: SyncContainer 구현](#3-step-2-synccontainer-구현)
4. [Step 3: DependencyResolver 구현](#4-step-3-dependencyresolver-구현)
5. [Step 4: 개별 SyncTask 구현](#5-step-4-개별-synctask-구현)
6. [Step 5: SyncOrchestrator 구현](#6-step-5-syncorchestrator-구현)
7. [Step 6: app.py sync 명령어 추가](#7-step-6-apppy-sync-명령어-추가)
8. [Step 7: 검증](#8-step-7-검증)
9. [검증 체크리스트](#9-검증-체크리스트)
10. [Phase 4 완료 기준](#10-phase-4-완료-기준)
11. [다음 단계](#11-다음-단계)

---

## 1. 개요

### 1.1 Phase 4 범위

Phase 4는 Data Syncer 컴포넌트를 구현하는 단계입니다. 기존 Puller(Phase 2)와 Merger(Phase 3)를 조합하여, 사용자가 CLI에서 특정 데이터를 지정하면 종속성을 자동 해결하고 Pull → Merge → DB 갱신을 수행합니다:

- **sync 명령어 추가**: `app.py sync {entity}` CLI subcommand
- **종속성 자동 해결**: 요청 entity의 상위 종속 데이터를 먼저 sync
- **입력 파라미터 설계**: `--competition-id`, `--season-id` 등 필수/선택 조합
- **DI Container 초기화**: Repository → Puller → Merger 파이프라인 연결
- **async 진입점**: `asyncio.run()` 기반 비동기 실행
- **실행 결과 요약**: 생성/갱신/스킵 건수 출력

### 1.2 현재 상태 (Phase 3 완료 후)

```
football_data_manager/
├── repository/                   # ✅ Phase 1 완료
│   ├── entities/                 # 15 Entity + 11 Association
│   ├── repositories/             # 15 Repository + base + pulselive
│   ├── session.py                # SessionFactory
│   └── container.py              # RepositoryContainer (17 providers)
├── puller/                       # ✅ Phase 2 완료
│   ├── interfaces/               # API response 모델
│   ├── clients/                  # HTTP/GraphQL 클라이언트
│   ├── pullers/                  # 11 Puller (10 Pulselive + 1 Athletic)
│   └── container.py              # PullerContainer (14 providers)
├── merger/                       # ✅ Phase 3 완료
│   ├── services/                 # TranslatorService, ResourceValidationClient
│   ├── mergers/                  # 11 Merger + GroundMerger
│   ├── scorer.py                 # PlayerStatScorer
│   └── container.py              # MergerContainer (17 providers)
├── syncer/                       # ✅ Phase 4 구현 완료 (통합 검증 제외)
│   ├── tasks/                    # 개별 entity sync 태스크
│   ├── dependency.py             # 종속성 해결기
│   ├── orchestrator.py           # sync 오케스트레이터
│   └── container.py              # SyncContainer
└── common/                       # 공통 서비스
    └── services/config/          # ConfigService
app.py                            # ✅ sync 명령어 추가 완료
```

### 1.3 Phase 4 완료 후 목표 구조

```
football_data_manager/
└── syncer/
    ├── __init__.py               # 비어 있음
    ├── tasks/
    │   ├── __init__.py           # 비어 있음
    │   ├── base.py               # AbstractSyncTask
    │   ├── competition.py        # CompetitionSyncTask
    │   ├── season.py             # SeasonSyncTask
    │   ├── team.py               # TeamSyncTask
    │   ├── player.py             # PlayerSyncTask
    │   ├── fixture.py            # FixtureSyncTask
    │   ├── match.py              # MatchSyncTask
    │   ├── match_stat.py         # MatchStatSyncTask
    │   ├── player_stat.py        # PlayerStatSyncTask
    │   ├── team_stat.py          # TeamStatSyncTask
    │   ├── award.py              # AwardSyncTask
    │   └── news.py               # NewsSyncTask
    ├── dependency.py             # DependencyResolver
    ├── orchestrator.py           # SyncOrchestrator
    └── container.py              # SyncContainer
```

### 1.4 파일 수 요약

| 디렉토리 | 파일 수 | 설명 |
|---------|---------|------|
| `syncer/` | 3 | dependency, orchestrator, container |
| `syncer/tasks/` | 12 | base + 11 entity sync task |
| 합계 | 15 | (+ `__init__.py` 2개) |

### 1.5 핵심 설계 결정

| 항목 | 결정 | 근거 |
|------|------|------|
| **종속성 해결** | 자동 해결 (DAG 기반) | 사용자가 종속성을 알 필요 없음 |
| **SyncTask 패턴** | 1 entity = 1 SyncTask 클래스 | 각 entity마다 pull/merge 호출 방식이 다름 |
| **실행 단위** | competition_id + season_id 기반 | 대부분의 API가 이 두 값을 필수로 요구 |
| **결과 추적** | SyncResult dataclass | 생성/갱신/스킵/오류 건수 집계 |
| **에러 전략** | 개별 entity 실패 시 계속 진행 | 전체 중단보다 부분 성공이 유용 |
| **News sync** | 독립 경로 (league_abbr 기반) | Pulselive API 종속성 없음, The Athletic 전용 |
| **세션 스코핑** | SyncTask별 독립 세션 | Identity Map 무한 성장 방지, 메모리 격리 |
| **배치 처리** | 대량 루프에 BATCH_SIZE 적용 (기본 50건) | 중간 커밋으로 메모리 피크 제한 |
| **Context 경량화** | Entity 전체 대신 ID만 보관 | ORM 객체 + Identity Map 추적 제거, 메모리 90%+ 절감 |
| **메모리 모니터링** | SyncTask 전후 RSS 로깅 | OOM 사전 감지 및 병목 식별 |

### 1.6 메모리 관리 전략

#### 문제 배경

PL 1시즌 full sync 시 약 1,300+ Entity 객체가 동시 생성됩니다 (1 Competition + 1 Season + 20 Teams + 500 Players + 380 Fixtures + 350 Matches + 20 Grounds). 특히 MatchEntity는 5개 Association 컬렉션 (Lineup, Card, Goal, Substitute, Substitution)을 포함하여 단일 객체가 무겁습니다. SQLAlchemy의 Identity Map이 모든 로드된 Entity를 추적하므로, 세션을 정리하지 않으면 메모리가 지속적으로 증가합니다.

#### 예상 메모리 사용량 (PL 1시즌 기준)

| 단계 | 누적 객체 수 | Entity 전체 보관 시 | ID만 보관 시 |
|------|------------|-------------------|-------------|
| Competition | 1 | ~1 KB | ~64 B |
| + Season | 2 | ~3 KB | ~128 B |
| + Team | 22 | ~63 KB | ~1.5 KB |
| + Player | 522 | ~3 MB | ~35 KB |
| + Fixture | 902 | ~3.8 MB | ~60 KB |
| + Match (+ associations) | 1,252+ | **~120 MB** | ~85 KB |
| **피크** | **~1,300+** | **~120-200 MB** | **~100 KB** |

#### 핵심 전략 4가지

**전략 1: SyncTask별 독립 세션 스코핑**

각 SyncTask가 자체 세션을 생성·종료합니다. 세션 종료 시 Identity Map이 자동 해제되어 이전 단계의 ORM 객체가 GC 대상이 됩니다.

```python
class TeamSyncTask(AbstractSyncTask):
    async def execute(self, context: SyncContext) -> SyncResult:
        async with self._session_factory() as session:
            # 이 세션에서만 Team pull → merge 수행
            ...
            await session.commit()
        # 세션 종료 → Identity Map 전체 해제
```

**전략 2: 배치 처리 + 중간 커밋**

대량 루프 (Player, Fixture, Match, MatchStat, PlayerStat) 에서 N건마다 커밋하고 세션을 갱신합니다.

```python
BATCH_SIZE = 50

async def execute(self, context: SyncContext) -> SyncResult:
    result = SyncResult(entity="match")
    for batch in chunked(context.fixture_ids, BATCH_SIZE):
        async with self._session_factory() as session:
            for fixture_id in batch:
                fixture = await fixture_repo.get(session, fixture_id)
                await self._merge_one(session, fixture)
                result.updated += 1
            await session.commit()
        # 배치 완료 → 세션 해제 → 메모리 회수
    return result
```

배치 크기 기준:

| SyncTask | 예상 반복 수 | 권장 BATCH_SIZE | 배치 수 |
|----------|------------|----------------|---------|
| PlayerSyncTask | ~500건 (20팀 × 25명) | 50 | ~10 |
| FixtureSyncTask | ~380건 (38MW × 10건) | 50 | ~8 |
| MatchSyncTask | ~350건 | 25 (API 4회/건) | ~14 |
| MatchStatSyncTask | ~350건 | 50 | ~7 |
| PlayerStatSyncTask | ~500건 | 50 | ~10 |

**전략 3: SyncContext 경량화 (ID만 보관)**

SyncContext에 Entity 전체 참조 대신 ID만 저장합니다. 다음 단계에서 필요할 때 세션 내에서 DB 조회합니다. DB 조회 비용은 있지만, 메모리 절감 효과가 압도적입니다 (~120 MB → ~100 KB).

```python
@dataclass
class SyncContext:
    """SyncTask 실행 간 공유되는 경량 컨텍스트. Entity 전체 대신 ID만 보관."""

    # 입력 파라미터
    competition_source_id: str | None = None
    season_source_id: str | None = None
    league_abbr: str = "EN_PR"

    # 이전 단계 결과 (ID만 보관, Entity 참조 X)
    competition_ids: list[int] = field(default_factory=list)
    season_ids: list[int] = field(default_factory=list)
    team_ids: list[int] = field(default_factory=list)
    player_ids: list[int] = field(default_factory=list)
    fixture_ids: list[int] = field(default_factory=list)
    match_ids: list[int] = field(default_factory=list)
    ground_ids: list[int] = field(default_factory=list)

    # source_id 매핑 (API 호출에 필요)
    team_source_ids: list[str] = field(default_factory=list)
    player_source_ids: list[str] = field(default_factory=list)
```

**전략 4: 메모리 모니터링 로깅**

각 SyncTask 실행 전후로 RSS 메모리를 로깅하여 이상 징후를 사전 감지합니다.

```python
import logging
import psutil

logger = logging.getLogger(__name__)

def log_memory(step: str) -> float:
    """현재 프로세스의 RSS 메모리를 MB 단위로 로깅."""
    rss_mb = psutil.Process().memory_info().rss / 1024 / 1024
    logger.info(f"[Memory] {step}: {rss_mb:.1f} MB")
    return rss_mb
```

#### 메모리 관리 체크리스트

- [ ] SyncTask별 독립 세션 스코핑 구현 (`async with session_factory()`)
- [x] 대량 SyncTask에 배치 처리 적용 (Player, Fixture, Match, MatchStat, PlayerStat)
- [x] `chunked()` 유틸리티 함수 구현 (또는 `more-itertools` 사용)
- [x] SyncContext를 ID 기반 경량 구조로 구현
- [x] SyncOrchestrator에 SyncTask 전후 메모리 로깅 추가
- [x] `psutil` 의존성 추가 (pyproject.toml)
- [ ] 통합 테스트에서 메모리 피크 확인 (PL 1시즌 기준 < 100 MB 목표)

---

## 2. Step 1: 데이터 종속성 그래프 설계

### 2.1 종속성 그래프 (DAG)

모든 entity 간의 종속성을 방향성 비순환 그래프(DAG)로 정의합니다. 특정 entity를 sync하려면 해당 entity의 **모든 상위 종속 entity가 먼저 존재**해야 합니다.

```
Level 0 (루트)     : Competition
                          │
Level 1            :    Season
                       /      \
Level 2         : Team       Fixture
                  │    \        │
Level 3       : Player  ┐    Match
                  │     │   /   │
Level 4       : PlayerStat  MatchStat
                  │
Level 5       : TeamStat ← (Match + Team + Fixture 종속)
                  │
Level 6       : Award ← (PlayerStat + Staff 종속)

별도 경로      : News ← (Team만 참조, 독립 데이터소스)
```

### 2.2 종속성 테이블

각 entity의 **직접 종속 entity**(sync 전에 반드시 존재해야 하는 데이터)를 정의합니다:

| Entity | 직접 종속 | 필수 입력 파라미터 | Puller 메서드 | Merger 메서드 |
|--------|----------|-------------------|--------------|--------------|
| **Competition** | (없음) | — | `CompetitionPuller.pull_competitions()` | `CompetitionMerger.merge()` |
| **Season** | Competition | `--competition-id` | `SeasonPuller.pull_seasons(comp_id)` | `SeasonMerger.merge(comp, resp)` |
| **Team** | Competition, Season | `--competition-id --season-id` | `TeamPuller.pull_teams(comp_id, season_id)` | `TeamMerger.merge(comp, season, resp)` |
| **Player** | Competition, Season, Team | `--competition-id --season-id` | `PlayerPuller.pull_squad(comp_id, season_id, team_id)` | `PlayerMerger.merge(comp, season, team, resp)` |
| **Fixture** | Season, Team | `--competition-id --season-id` | `FixturePuller.pull_matchweek_matches(comp_id, season_id, mw)` | `FixtureMerger.merge(season, mw, resp)` |
| **Match** | Fixture, Team, Player | `--competition-id --season-id` | `MatchMerger.merge_from_api(fixture, comp, season)` | (Merger가 내부적으로 pull) |
| **MatchStat** | Match | `--competition-id --season-id` | `MatchStatPuller.pull_match_stat(match_id)` | `MatchStatMerger.merge(match, resp)` |
| **PlayerStat** | Player, Competition, Season | `--competition-id --season-id` | `PlayerStatMerger.merge(player, comp, season)` | (Merger가 내부적으로 pull) |
| **TeamStat** | Team, Match, Fixture, Competition, Season | `--competition-id --season-id` | `TeamStatMerger.merge(team, comp, season, ground)` | (Merger가 내부적으로 pull+계산) |
| **Award** | Competition, Season, PlayerStat, Staff | `--competition-id --season-id` | `AwardPuller.pull_awards(comp_id, season_id)` | `AwardMerger.merge(comp, season, resp)` |
| **News** | Team (참조만) | `--league-abbr` (기본값: EN_PR) | `NewsPuller.pull_league_feed(league)` | `NewsMerger.merge_league_feed(league)` |

### 2.3 종속성 해결 순서 (Sync Level)

사용자가 특정 entity를 요청하면, DependencyResolver가 해당 entity의 **전체 종속 체인**을 resolve하여 실행 순서를 결정합니다:

| 요청 Entity | 실행 순서 (자동 해결) |
|------------|---------------------|
| `competition` | Competition |
| `season` | Competition → Season |
| `team` | Competition → Season → Team |
| `player` | Competition → Season → Team → Player |
| `fixture` | Competition → Season → Team → Fixture |
| `match` | Competition → Season → Team → Player → Fixture → Match |
| `match-stat` | Competition → Season → Team → Player → Fixture → Match → MatchStat |
| `player-stat` | Competition → Season → Team → Player → PlayerStat |
| `team-stat` | Competition → Season → Team → Player → Fixture → Match → TeamStat |
| `award` | Competition → Season → Team → Player → Fixture → Match → PlayerStat → Award |
| `news` | News (독립, Team은 DB 기존 데이터 참조) |
| `all` | Competition → Season → Team → Player → Fixture → Match → MatchStat → PlayerStat → TeamStat → Award → News |

### 2.4 체크리스트

- [x] 종속성 그래프(DAG) 코드 정의 (`DEPENDENCY_GRAPH` dict)
- [x] 사이클 없음 검증 (위상 정렬 가능)
- [x] `all` 요청 시 전체 순서 결정 로직

---

## 3. Step 2: SyncContainer 구현

### 3.1 설명

`SyncContainer`는 기존 3개 Container(Repository, Puller, Merger)를 조합하여 Syncer 계층에서 사용할 수 있도록 합니다.

### 3.2 파일: `syncer/container.py`

```python
from dependency_injector import containers, providers
from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.merger.container import MergerContainer
from football_data_manager.puller.container import PullerContainer
from football_data_manager.repository.container import RepositoryContainer


class SyncContainer(containers.DeclarativeContainer):
    """DI container for the sync layer."""

    config_service = providers.Dependency(instance_of=ConfigService)

    repository_container = providers.Container(
        RepositoryContainer,
        config_service=config_service,
    )
    puller_container = providers.Container(
        PullerContainer,
        config=config_service.provided.api_list,
    )
    merger_container = providers.Container(
        MergerContainer,
        config_service=config_service,
        repository_container=repository_container,
        puller_container=puller_container,
    )
```

### 3.3 초기화 패턴

```python
async def create_sync_container() -> SyncContainer:
    config_service = ConfigService()
    container = SyncContainer(config_service=config_service)
    # 연결 검증
    session_factory = container.repository_container().session_factory()
    await session_factory.check_connection()
    return container
```

### 3.4 체크리스트

- [x] `syncer/__init__.py` 생성 (비어 있음)
- [x] `syncer/container.py` 구현
- [x] 3개 하위 Container 연결 검증 (import + wire)
- [x] `ConfigService` → `PullerContainer.config` 매핑 확인

---

## 4. Step 3: DependencyResolver 구현

### 4.1 설명

사용자가 요청한 entity의 종속 체인을 자동 해결하여 실행 순서를 반환합니다. 위상 정렬(topological sort) 기반으로 동작합니다.

### 4.2 파일: `syncer/dependency.py`

```python
from enum import StrEnum


class SyncEntity(StrEnum):
    """Sync 대상 entity 목록."""
    COMPETITION = "competition"
    SEASON = "season"
    TEAM = "team"
    PLAYER = "player"
    FIXTURE = "fixture"
    MATCH = "match"
    MATCH_STAT = "match-stat"
    PLAYER_STAT = "player-stat"
    TEAM_STAT = "team-stat"
    AWARD = "award"
    NEWS = "news"


# 종속성 그래프: entity → 직접 종속 entity 목록
DEPENDENCY_GRAPH: dict[SyncEntity, list[SyncEntity]] = {
    SyncEntity.COMPETITION: [],
    SyncEntity.SEASON: [SyncEntity.COMPETITION],
    SyncEntity.TEAM: [SyncEntity.COMPETITION, SyncEntity.SEASON],
    SyncEntity.PLAYER: [SyncEntity.TEAM],
    SyncEntity.FIXTURE: [SyncEntity.SEASON, SyncEntity.TEAM],
    SyncEntity.MATCH: [SyncEntity.FIXTURE, SyncEntity.PLAYER],
    SyncEntity.MATCH_STAT: [SyncEntity.MATCH],
    SyncEntity.PLAYER_STAT: [SyncEntity.PLAYER],
    SyncEntity.TEAM_STAT: [SyncEntity.MATCH, SyncEntity.TEAM],
    SyncEntity.AWARD: [SyncEntity.PLAYER_STAT],
    SyncEntity.NEWS: [],  # 독립 경로
}


class DependencyResolver:
    """종속성 자동 해결기."""

    @staticmethod
    def resolve(target: SyncEntity) -> list[SyncEntity]:
        """target entity를 sync하기 위해 필요한 전체 entity 목록을 실행 순서대로 반환."""
        ...

    @staticmethod
    def resolve_all() -> list[SyncEntity]:
        """모든 entity를 종속성 순서대로 반환."""
        ...
```

### 4.3 resolve 예시

```python
DependencyResolver.resolve(SyncEntity.TEAM_STAT)
# → [COMPETITION, SEASON, TEAM, PLAYER, FIXTURE, MATCH, TEAM_STAT]

DependencyResolver.resolve(SyncEntity.PLAYER_STAT)
# → [COMPETITION, SEASON, TEAM, PLAYER, PLAYER_STAT]

DependencyResolver.resolve(SyncEntity.NEWS)
# → [NEWS]
```

### 4.4 체크리스트

- [x] `SyncEntity` enum 정의 (11개 entity)
- [x] `DEPENDENCY_GRAPH` dict 정의
- [x] `DependencyResolver.resolve()` 구현 (위상 정렬)
- [x] `DependencyResolver.resolve_all()` 구현
- [x] 사이클 감지 방어 코드
- [x] 단위 테스트: 각 entity별 resolve 결과 검증

---

## 5. Step 4: 개별 SyncTask 구현

### 5.1 설명

각 entity별로 Pull → Merge 파이프라인을 캡슐화한 SyncTask 클래스를 구현합니다. SyncTask는 `SyncOrchestrator`에 의해 종속성 순서대로 호출됩니다.

### 5.2 SyncResult 데이터 모델

```python
from dataclasses import dataclass, field


@dataclass
class SyncResult:
    """Sync 실행 결과."""
    entity: str
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    messages: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.created + self.updated + self.skipped

    @property
    def success(self) -> bool:
        return self.errors == 0
```

### 5.3 AbstractSyncTask (base.py)

```python
from abc import ABC, abstractmethod

from football_data_manager.repository.session import SessionFactory


class AbstractSyncTask(ABC):
    """모든 SyncTask의 추상 기반 클래스.

    각 SyncTask는 session_factory를 주입받아 독립 세션을 생성합니다.
    세션 종료 시 Identity Map이 자동 해제되어 OOM을 방지합니다.
    """

    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory

    @abstractmethod
    async def execute(self, context: SyncContext) -> SyncResult:
        """entity를 pull → merge하여 DB에 반영한다.

        구현 시 반드시 `async with self._session_factory()` 블록 내에서
        DB 작업을 수행하여 세션 스코핑을 보장해야 합니다.
        대량 루프가 있는 경우 BATCH_SIZE 단위로 세션을 나누어야 합니다.
        """
        ...
```

### 5.4 SyncContext 데이터 모델

SyncTask 간에 공유되는 **경량** 실행 컨텍스트입니다. OOM 방지를 위해 Entity 전체 참조 대신 **ID만 보관**합니다. 다음 단계의 SyncTask가 실제 Entity가 필요하면 자체 세션에서 DB 조회합니다.

> **설계 근거**: Entity 전체 보관 시 PL 1시즌 기준 ~120-200 MB가 SyncContext에 누적됩니다. ID만 보관하면 ~100 KB로 1,000배 이상 절감됩니다. DB 재조회 비용 (PK 기반 단건 조회)은 무시할 수 있는 수준입니다. 자세한 분석은 [1.6 메모리 관리 전략](#16-메모리-관리-전략)을 참고하세요.

```python
from dataclasses import dataclass, field


@dataclass
class SyncContext:
    """SyncTask 실행 간 공유되는 경량 컨텍스트.

    OOM 방지를 위해 Entity 전체 참조 대신 ID만 보관합니다.
    다음 단계 SyncTask에서 Entity가 필요하면 자체 세션에서 DB 조회합니다.
    """

    # 입력 파라미터
    competition_source_id: str | None = None
    season_source_id: str | None = None
    league_abbr: str = "EN_PR"

    # 이전 단계 결과 — PK (DB id) 보관
    competition_ids: list[int] = field(default_factory=list)
    season_ids: list[int] = field(default_factory=list)
    team_ids: list[int] = field(default_factory=list)
    player_ids: list[int] = field(default_factory=list)
    fixture_ids: list[int] = field(default_factory=list)
    match_ids: list[int] = field(default_factory=list)
    ground_ids: list[int] = field(default_factory=list)

    # source_id 매핑 — API 호출에 필요한 외부 ID
    # (PK만으로는 API를 호출할 수 없으므로 source_id도 함께 보관)
    competition_source_ids: list[str] = field(default_factory=list)
    season_source_ids: list[str] = field(default_factory=list)
    team_source_ids: list[str] = field(default_factory=list)
```

### 5.5 개별 SyncTask 구현 (11개)

각 SyncTask는 **DI Container에서 Puller/Merger를 주입**받고, SyncContext를 통해 이전 단계 결과를 참조합니다.

#### CompetitionSyncTask (소량 — 세션 1회)

```python
class CompetitionSyncTask(AbstractSyncTask):
    def __init__(
        self, session_factory: SessionFactory,
        puller: CompetitionPuller, merger: CompetitionMerger,
    ): ...

    async def execute(self, context: SyncContext) -> SyncResult:
        """
        소량 데이터 (1~수십 건)이므로 단일 세션으로 처리.

        1. CompetitionPuller.pull_competitions() 호출
        2. async with self._session_factory() 세션 열기
        3. CompetitionMerger.merge(response) 호출
        4. context.competition_source_id가 지정된 경우 해당 competition만 필터
        5. 결과의 PK/source_id를 context.competition_ids, competition_source_ids에 저장
        6. session.commit() → 세션 종료
        """
```

#### SeasonSyncTask (소량 — 세션 1회)

```python
class SeasonSyncTask(AbstractSyncTask):
    def __init__(
        self, session_factory: SessionFactory,
        puller: SeasonPuller, merger: SeasonMerger,
    ): ...

    async def execute(self, context: SyncContext) -> SyncResult:
        """
        소량 데이터이므로 단일 세션으로 처리.

        context.competition_source_ids 각각에 대해:
        1. SeasonPuller.pull_seasons(comp_source_id) 호출
        2. async with self._session_factory() 세션 열기
        3. SeasonMerger.merge(comp, response) 호출
        4. context.season_source_id가 지정된 경우 해당 season만 필터
        5. 결과의 PK/source_id를 context.season_ids, season_source_ids에 저장
        6. session.commit() → 세션 종료
        """
```

#### TeamSyncTask (소량 — 세션 1회)

```python
class TeamSyncTask(AbstractSyncTask):
    def __init__(
        self, session_factory: SessionFactory,
        puller: TeamPuller, merger: TeamMerger,
    ): ...

    async def execute(self, context: SyncContext) -> SyncResult:
        """
        소량 데이터 (~20팀)이므로 단일 세션으로 처리.

        context.competition_source_ids × context.season_source_ids 조합에 대해:
        1. TeamPuller.pull_teams(comp_source_id, season_source_id) 호출
        2. async with self._session_factory() 세션 열기
        3. TeamMerger.merge(comp, season, response) 호출
        4. 결과의 PK/source_id를 context.team_ids, team_source_ids에 저장
        5. Ground PK를 context.ground_ids에 저장
        6. session.commit() → 세션 종료
        """
```

#### PlayerSyncTask (대량 ~500건 — 배치 처리)

```python
class PlayerSyncTask(AbstractSyncTask):
    """~500명 (20팀 × 25명). 팀 단위로 세션을 나누어 배치 처리."""

    BATCH_SIZE = 5  # 팀 단위 배치 (5팀 × ~25명 = ~125명/배치)

    def __init__(
        self, session_factory: SessionFactory,
        puller: PlayerPuller, merger: PlayerMerger,
    ): ...

    async def execute(self, context: SyncContext) -> SyncResult:
        """
        팀을 BATCH_SIZE 단위로 묶어 배치 처리.

        for team_batch in chunked(context.team_source_ids, BATCH_SIZE):
            async with self._session_factory() as session:
                for team_source_id in team_batch:
                    1. PlayerPuller.pull_squad(comp_source_id, season_source_id, team_source_id) 호출
                    2. PlayerMerger.merge(comp, season, team, response) 호출
                    3. 결과의 PK를 context.player_ids에 추가
                await session.commit()
            # 배치 완료 → 세션 해제 → Identity Map 회수
        """
```

#### FixtureSyncTask (대량 ~380건 — 배치 처리)

```python
class FixtureSyncTask(AbstractSyncTask):
    """~380건 (38MW × 10건). matchweek 단위로 세션을 나누어 배치 처리."""

    BATCH_SIZE = 5  # matchweek 단위 배치 (5MW × ~10건 = ~50건/배치)

    def __init__(
        self, session_factory: SessionFactory,
        puller: FixturePuller, merger: FixtureMerger,
    ): ...

    async def execute(self, context: SyncContext) -> SyncResult:
        """
        matchweek를 BATCH_SIZE 단위로 묶어 배치 처리.

        for mw_batch in chunked(range(1, 39), BATCH_SIZE):
            async with self._session_factory() as session:
                for mw in mw_batch:
                    1. FixturePuller.pull_matchweek_matches(comp_source_id, season_source_id, mw) 호출
                    2. FixtureMerger.merge(season, mw, response) 호출
                    3. 결과의 PK를 context.fixture_ids에 추가
                await session.commit()
            # 배치 완료 → 세션 해제
        """
```

#### MatchSyncTask (대량 ~350건 — 배치 처리, 가장 무거움)

```python
class MatchSyncTask(AbstractSyncTask):
    """~350건, 건당 4 API 호출 + 5개 Association. 가장 메모리 집약적.

    BATCH_SIZE를 작게 설정하여 세션을 자주 갱신합니다.
    """

    BATCH_SIZE = 25  # 25건 × 4 API = 100 API 호출/배치

    def __init__(
        self, session_factory: SessionFactory,
        merger: MatchMerger,
    ): ...

    async def execute(self, context: SyncContext) -> SyncResult:
        """
        fixture_ids를 BATCH_SIZE 단위로 묶어 배치 처리.

        for fixture_batch in chunked(context.fixture_ids, BATCH_SIZE):
            async with self._session_factory() as session:
                for fixture_id in fixture_batch:
                    1. DB에서 fixture 조회 (세션 내 PK 조회)
                    2. MatchMerger.merge_from_api(fixture, comp, season) 호출
                       (MatchMerger가 내부적으로 4개 API pull 수행)
                    3. 결과의 PK를 context.match_ids에 추가
                await session.commit()
            # 배치 완료 → 세션 해제 → Match + 5개 Association의 Identity Map 전체 해제
        참고: period != FULLTIME인 경기는 merge_from_api 내에서 skip 처리
        """
```

#### MatchStatSyncTask (대량 ~350건 — 배치 처리)

```python
class MatchStatSyncTask(AbstractSyncTask):
    """~350건. 건당 API 1회 + 330+ stat 필드 파싱."""

    BATCH_SIZE = 50

    def __init__(
        self, session_factory: SessionFactory,
        puller: MatchStatPuller, merger: MatchStatMerger,
    ): ...

    async def execute(self, context: SyncContext) -> SyncResult:
        """
        match_ids (FULLTIME만)를 BATCH_SIZE 단위로 묶어 배치 처리.

        for match_batch in chunked(fulltime_match_ids, BATCH_SIZE):
            async with self._session_factory() as session:
                for match_id in match_batch:
                    1. DB에서 match 조회 (PK 조회)
                    2. MatchStatPuller.pull_match_stat(match.source_id) 호출
                    3. MatchStatMerger.merge(match, response) 호출
                await session.commit()
            # 배치 완료 → 세션 해제
        """
```

#### PlayerStatSyncTask (대량 ~500건 — 배치 처리)

```python
class PlayerStatSyncTask(AbstractSyncTask):
    """~500건. 건당 API 호출 + 6개 점수 계산."""

    BATCH_SIZE = 50

    def __init__(
        self, session_factory: SessionFactory,
        merger: PlayerStatMerger, scorer: PlayerStatScorer,
    ): ...

    async def execute(self, context: SyncContext) -> SyncResult:
        """
        player_ids를 BATCH_SIZE 단위로 묶어 배치 처리.

        for player_batch in chunked(context.player_ids, BATCH_SIZE):
            async with self._session_factory() as session:
                for player_id in player_batch:
                    1. DB에서 player 조회 (PK 조회)
                    2. PlayerStatMerger.merge(player, comp, season) 호출
                    3. PlayerStatScorer.score(player_stat) 호출하여 6개 점수 계산
                    4. DB에 score 반영
                await session.commit()
            # 배치 완료 → 세션 해제
        """
```

#### TeamStatSyncTask (소량 ~20건 — 세션 1회)

```python
class TeamStatSyncTask(AbstractSyncTask):
    """~20건. 단일 세션으로 충분하나, 내부적으로 Match 조회가 무거울 수 있음."""

    def __init__(
        self, session_factory: SessionFactory,
        merger: TeamStatMerger,
    ): ...

    async def execute(self, context: SyncContext) -> SyncResult:
        """
        소량이므로 단일 세션. 단, TeamStatMerger 내부에서 Match 대량 조회 시
        session.expire_all() 호출로 중간 정리.

        async with self._session_factory() as session:
            for team_id in context.team_ids:
                1. DB에서 team, ground 조회 (PK 조회)
                2. TeamStatMerger.merge(team, comp, season, ground) 호출
                   (내부적으로 Phase 1 DB계산 + Phase 2 API pull 수행)
                3. session.expire_all()  # 중간 정리 (TeamStat 내부에서 로드된 Match 객체 해제)
            await session.commit()
        """
```

#### AwardSyncTask (소량 — 세션 1회)

```python
class AwardSyncTask(AbstractSyncTask):
    def __init__(
        self, session_factory: SessionFactory,
        puller: AwardPuller, merger: AwardMerger,
    ): ...

    async def execute(self, context: SyncContext) -> SyncResult:
        """
        소량 데이터이므로 단일 세션으로 처리.

        async with self._session_factory() as session:
            for comp_source_id, season_source_id in comp_season_pairs:
                1. AwardPuller.pull_awards(comp_source_id, season_source_id) 호출
                2. AwardMerger.merge(comp, season, response) 호출
            await session.commit()
        """
```

#### NewsSyncTask (독립 — 세션 1회)

```python
class NewsSyncTask(AbstractSyncTask):
    def __init__(
        self, session_factory: SessionFactory,
        merger: NewsMerger,
    ): ...

    async def execute(self, context: SyncContext) -> SyncResult:
        """
        독립 데이터소스. 단일 세션으로 처리.

        async with self._session_factory() as session:
            1. NewsMerger.merge_league_feed(context.league_abbr) 호출
               (NewsMerger가 내부적으로 feed pull + scrape + translate 수행)
            await session.commit()
        2. NewsMerger.close() 호출하여 리소스 해제
        참고: News는 독립 데이터소스(The Athletic)로 다른 entity와 종속성 없음
        """
```

### 5.6 체크리스트

- [x] `syncer/tasks/__init__.py` 생성 (비어 있음)
- [x] `syncer/tasks/base.py`: `AbstractSyncTask` (session_factory 주입), `SyncResult`, `SyncContext` (ID 기반 경량) 구현
- [x] `chunked()` 유틸리티 함수 구현 (또는 `more-itertools` 의존성 추가)
- [x] `syncer/tasks/competition.py`: `CompetitionSyncTask` 구현 (단일 세션)
- [x] `syncer/tasks/season.py`: `SeasonSyncTask` 구현 (단일 세션)
- [x] `syncer/tasks/team.py`: `TeamSyncTask` 구현 (단일 세션)
- [x] `syncer/tasks/player.py`: `PlayerSyncTask` 구현 (**배치 처리**, BATCH_SIZE=5팀)
- [x] `syncer/tasks/fixture.py`: `FixtureSyncTask` 구현 (**배치 처리**, BATCH_SIZE=5MW)
- [x] `syncer/tasks/match.py`: `MatchSyncTask` 구현 (**배치 처리**, BATCH_SIZE=25건)
- [x] `syncer/tasks/match_stat.py`: `MatchStatSyncTask` 구현 (**배치 처리**, BATCH_SIZE=50건)
- [x] `syncer/tasks/player_stat.py`: `PlayerStatSyncTask` 구현 (**배치 처리**, BATCH_SIZE=50건)
- [x] `syncer/tasks/team_stat.py`: `TeamStatSyncTask` 구현 (단일 세션 + expire_all 중간 정리)
- [x] `syncer/tasks/award.py`: `AwardSyncTask` 구현 (단일 세션)
- [x] `syncer/tasks/news.py`: `NewsSyncTask` 구현 (단일 세션)
- [x] 모든 SyncTask에 `session_factory` 주입 확인
- [x] 대량 SyncTask (Player, Fixture, Match, MatchStat, PlayerStat) 배치 처리 동작 확인

---

## 6. Step 5: SyncOrchestrator 구현

### 6.1 설명

`SyncOrchestrator`는 DependencyResolver의 결과를 바탕으로 SyncTask를 순서대로 실행하고, 결과를 집계합니다.

### 6.2 파일: `syncer/orchestrator.py`

```python
import logging
import psutil

logger = logging.getLogger(__name__)


def _log_memory(step: str) -> float:
    """현재 프로세스의 RSS 메모리(MB)를 로깅하고 반환."""
    rss_mb = psutil.Process().memory_info().rss / 1024 / 1024
    logger.info(f"[Memory] {step}: {rss_mb:.1f} MB")
    return rss_mb


class SyncOrchestrator:
    """Sync 실행 오케스트레이터.

    각 SyncTask 실행 전후로 메모리 사용량을 로깅합니다.
    SyncTask는 각자 독립 세션을 사용하므로, 이전 단계의 ORM 객체가
    메모리에 누적되지 않습니다.
    """

    def __init__(self, container: SyncContainer):
        self._container = container

    async def sync(
        self,
        target: SyncEntity,
        competition_source_id: str | None = None,
        season_source_id: str | None = None,
        league_abbr: str = "EN_PR",
    ) -> list[SyncResult]:
        """
        target entity를 sync한다.

        1. DependencyResolver.resolve(target) 로 실행 순서 결정
        2. SyncContext 생성 (입력 파라미터 설정)
        3. 각 entity에 대응하는 SyncTask를 순서대로 실행
           - 각 step 전후로 _log_memory() 호출
           - SyncTask 내부에서 세션 스코핑 + 배치 처리 수행
        4. 각 step의 SyncResult를 수집하여 반환
        5. 개별 entity 실패 시 에러 로깅 후 다음 entity 계속 진행
        """
        ...

    async def sync_all(
        self,
        competition_source_id: str | None = None,
        season_source_id: str | None = None,
    ) -> list[SyncResult]:
        """모든 entity를 종속성 순서대로 sync."""
        ...

    def _create_task(self, entity: SyncEntity) -> AbstractSyncTask:
        """DI Container에서 해당 entity의 SyncTask를 생성.

        모든 SyncTask에 session_factory를 주입합니다.
        """
        ...

    @staticmethod
    def print_summary(results: list[SyncResult]) -> None:
        """실행 결과 요약을 터미널에 출력."""
        ...
```

### 6.3 실행 흐름

```
사용자 입력: python app.py sync team-stat --competition-id 1 --season-id 578

1. DependencyResolver.resolve(TEAM_STAT)
   → [COMPETITION, SEASON, TEAM, PLAYER, FIXTURE, MATCH, TEAM_STAT]

2. SyncContext 생성 (경량 — ID만 보관):
   - competition_source_id = "1"
   - season_source_id = "578"

3. 순차 실행 (각 step 전후 메모리 로깅):

   [Memory] Before competition: 45.2 MB
   Step 1/7: CompetitionSyncTask.execute(ctx) — 단일 세션
     → Pull competitions → Filter id="1"
     → ctx.competition_ids = [3], ctx.competition_source_ids = ["1"]
     → SyncResult(entity="competition", created=0, updated=1)
   [Memory] After competition: 46.1 MB (+0.9 MB)

   [Memory] Before season: 46.1 MB
   Step 2/7: SeasonSyncTask.execute(ctx) — 단일 세션
     → Pull seasons for comp "1" → Filter id="578"
     → ctx.season_ids = [12], ctx.season_source_ids = ["578"]
     → SyncResult(entity="season", created=0, updated=1)
   [Memory] After season: 46.3 MB (+0.2 MB)

   [Memory] Before team: 46.3 MB
   Step 3/7: TeamSyncTask.execute(ctx) — 단일 세션
     → Pull teams → ctx.team_ids = [20개 PK], ctx.team_source_ids = [20개]
     → SyncResult(entity="team", created=0, updated=20)
   [Memory] After team: 47.0 MB (+0.7 MB)

   [Memory] Before player: 47.0 MB
   Step 4/7: PlayerSyncTask.execute(ctx) — 배치 처리 (5팀/배치 × 4배치)
     → 배치 1: 5팀 squad pull → merge → commit → 세션 해제
     → 배치 2: 5팀 squad pull → merge → commit → 세션 해제
     → 배치 3: 5팀 squad pull → merge → commit → 세션 해제
     → 배치 4: 5팀 squad pull → merge → commit → 세션 해제
     → ctx.player_ids = [500개 PK]
     → SyncResult(entity="player", created=15, updated=485)
   [Memory] After player: 48.5 MB (+1.5 MB) ← 배치 처리 덕분에 피크 억제

   [Memory] Before fixture: 48.5 MB
   Step 5/7: FixtureSyncTask.execute(ctx) — 배치 처리 (5MW/배치 × 8배치)
     → 배치 1-8: matchweek별 pull → merge → commit → 세션 해제
     → ctx.fixture_ids = [380개 PK]
     → SyncResult(entity="fixture", created=10, updated=370)
   [Memory] After fixture: 49.2 MB (+0.7 MB)

   [Memory] Before match: 49.2 MB
   Step 6/7: MatchSyncTask.execute(ctx) — 배치 처리 (25건/배치 × 14배치)
     → 배치 1-14: fixture별 4 API call → merge → commit → 세션 해제
     → ctx.match_ids = [350개 PK]
     → SyncResult(entity="match", created=10, updated=340, skipped=30)
   [Memory] After match: 52.0 MB (+2.8 MB) ← 가장 무거운 단계이나 피크 제한됨

   [Memory] Before team-stat: 52.0 MB
   Step 7/7: TeamStatSyncTask.execute(ctx) — 단일 세션 (20건)
     → Merge team stats + expire_all() 중간 정리
     → SyncResult(entity="team-stat", created=0, updated=20)
   [Memory] After team-stat: 52.5 MB (+0.5 MB)

4. 결과 출력:
   ┌─────────────┬─────────┬─────────┬─────────┬────────┬──────────┐
   │ Entity      │ Created │ Updated │ Skipped │ Errors │ Mem (MB) │
   ├─────────────┼─────────┼─────────┼─────────┼────────┼──────────┤
   │ competition │       0 │       1 │       0 │      0 │     +0.9 │
   │ season      │       0 │       1 │       0 │      0 │     +0.2 │
   │ team        │       0 │      20 │       0 │      0 │     +0.7 │
   │ player      │      15 │     485 │       0 │      0 │     +1.5 │
   │ fixture     │      10 │     370 │       0 │      0 │     +0.7 │
   │ match       │      10 │     340 │      30 │      0 │     +2.8 │
   │ team-stat   │       0 │      20 │       0 │      0 │     +0.5 │
   ├─────────────┼─────────┼─────────┼─────────┼────────┼──────────┤
   │ Total       │      35 │    1237 │      30 │      0 │     +7.3 │
   └─────────────┴─────────┴─────────┴─────────┴────────┴──────────┘
   Peak memory: 52.5 MB (baseline: 45.2 MB)
   ✅ Sync completed successfully.
```

> **비교**: 메모리 관리 없이 Entity 전체를 SyncContext에 누적했을 경우, 피크 메모리는 ~200-300 MB에 달했을 것입니다. 배치 처리 + ID 기반 Context + 세션 스코핑으로 피크를 ~52 MB로 제한합니다.

### 6.4 에러 핸들링

```python
# 개별 entity 실패 시 전략
for i, entity in enumerate(execution_order):
    _log_memory(f"Before {entity.value}")
    try:
        task = self._create_task(entity)
        result = await task.execute(context)
        results.append(result)
    except Exception as e:
        logger.error(f"Sync failed for {entity}: {e}")
        results.append(SyncResult(
            entity=entity.value,
            errors=1,
            messages=[str(e)],
        ))
        # SyncTask 내부에서 세션을 관리하므로, 실패 시에도 세션은 자동 rollback됨
        # (async with 블록의 __aexit__이 예외 시 rollback 수행)

        # 실패한 entity의 종속 entity도 skip 처리
        if is_dependency_of_remaining(entity, remaining_entities):
            logger.warning(f"Skipping dependent entities due to {entity} failure")
            break
    finally:
        _log_memory(f"After {entity.value}")
```

> **세션 안전성**: 각 SyncTask가 `async with self._session_factory()` 블록 내에서 작업하므로, 예외 발생 시 해당 세션만 rollback됩니다. 다른 SyncTask의 이전 커밋은 영향받지 않습니다. 배치 처리 중 실패 시에도 이미 커밋된 배치는 보존됩니다.

### 6.5 체크리스트

- [x] `syncer/orchestrator.py`: `SyncOrchestrator` 구현
- [x] `sync()` 메서드: 단일 entity + 종속성 자동 해결
- [x] `sync_all()` 메서드: 전체 entity sync
- [x] `_create_task()` 메서드: DI Container → SyncTask 매핑 (session_factory 주입 포함)
- [x] `print_summary()` 메서드: 결과 테이블 출력 (메모리 사용량 컬럼 포함)
- [x] `_log_memory()` 함수: SyncTask 전후 RSS 메모리 로깅
- [x] 에러 핸들링: 개별 실패 시 계속 진행 또는 종속 실패 시 중단
- [ ] 세션 안전성: 실패 시 해당 SyncTask 세션만 rollback, 이전 커밋 보존 확인
- [x] `psutil` 의존성 추가 (pyproject.toml)

---

## 7. Step 6: app.py sync 명령어 추가

### 7.1 설명

`app.py`에 `sync` subcommand를 추가합니다. 기존 `health`, `run`, `pull-data` 명령어와 동일한 구조를 따릅니다.

### 7.2 CLI 인터페이스 설계

```bash
# 기본 사용법
python app.py sync {entity} [OPTIONS]

# Entity 목록
competition, season, team, player, fixture, match,
match-stat, player-stat, team-stat, award, news, all

# 공통 옵션
--competition-id ID    # Pulselive competition source_id (예: "1" = Premier League)
--season-id ID         # Pulselive season source_id (예: "578" = 2024/25)
--league-abbr ABBR     # The Athletic league abbreviation (기본값: EN_PR, news 전용)

# 사용 예시
python app.py sync competition                          # 전체 competition 동기화
python app.py sync season --competition-id 1            # PL의 전체 season 동기화
python app.py sync team --competition-id 1 --season-id 578  # PL 24/25 팀 동기화
python app.py sync team-stat --competition-id 1 --season-id 578  # 종속성 자동 해결 후 team-stat까지
python app.py sync all --competition-id 1 --season-id 578  # 전체 데이터 동기화
python app.py sync news                                 # The Athletic 뉴스 동기화
python app.py sync news --league-abbr EN_PR             # 특정 리그 뉴스 동기화
```

### 7.3 app.py 수정 사항

```python
# sync subcommand 추가
sync_parser = subparsers.add_parser("sync", help="Sync entity data (Pull → Merge → DB)")
sync_parser.add_argument(
    "entity",
    choices=[
        "competition", "season", "team", "player", "fixture",
        "match", "match-stat", "player-stat", "team-stat",
        "award", "news", "all",
    ],
    help="Target entity to sync (dependencies auto-resolved)",
)
sync_parser.add_argument("--competition-id", help="Pulselive competition source ID")
sync_parser.add_argument("--season-id", help="Pulselive season source ID")
sync_parser.add_argument("--league-abbr", default="EN_PR", help="League abbreviation for news (default: EN_PR)")


# Handler
async def sync_data(entity: str, competition_id: str | None, season_id: str | None, league_abbr: str) -> int:
    from football_data_manager.syncer.container import SyncContainer
    from football_data_manager.syncer.dependency import SyncEntity
    from football_data_manager.syncer.orchestrator import SyncOrchestrator
    from football_data_manager.common.services.config.config_service import ConfigService

    config_service = ConfigService()
    container = SyncContainer(config_service=config_service)

    orchestrator = SyncOrchestrator(container)

    target = SyncEntity(entity) if entity != "all" else None
    if target:
        results = await orchestrator.sync(
            target=target,
            competition_source_id=competition_id,
            season_source_id=season_id,
            league_abbr=league_abbr,
        )
    else:
        results = await orchestrator.sync_all(
            competition_source_id=competition_id,
            season_source_id=season_id,
        )

    orchestrator.print_summary(results)
    return 0 if all(r.success for r in results) else 1


# main() 내 라우팅
elif args.command == "sync":
    import asyncio
    return asyncio.run(sync_data(
        args.entity, args.competition_id, args.season_id, args.league_abbr,
    ))
```

### 7.4 입력 파라미터 검증

| Entity | `--competition-id` | `--season-id` | `--league-abbr` |
|--------|-------------------|---------------|-----------------|
| competition | 선택 (필터용) | — | — |
| season | 필수 | 선택 (필터용) | — |
| team~award | 필수 | 필수 | — |
| news | — | — | 선택 (기본 EN_PR) |
| all | 필수 | 필수 | — |

```python
# 검증 로직
def _validate_sync_args(entity: str, competition_id: str | None, season_id: str | None):
    needs_competition = entity not in ("competition", "news")
    needs_season = entity not in ("competition", "season", "news")

    if needs_competition and not competition_id:
        print(f"Error: --competition-id is required for '{entity}'")
        sys.exit(1)
    if needs_season and not season_id:
        print(f"Error: --season-id is required for '{entity}'")
        sys.exit(1)
```

### 7.5 체크리스트

- [x] `app.py`에 `sync` subparser 추가
- [x] `sync_data()` async handler 구현
- [x] `_validate_sync_args()` 입력 검증 구현
- [x] `asyncio.run()` 진입점 처리
- [x] 기존 `pull-data` 명령어는 유지 (향후 deprecated 또는 제거)
- [x] help 메시지 및 epilog 업데이트

---

## 8. Step 7: 검증

### 8.1 단위 테스트

```bash
# 테스트 파일 구조
tests/
└── syncer/
    ├── __init__.py
    ├── test_dependency.py          # DependencyResolver 단위 테스트
    ├── test_sync_context.py        # SyncContext/SyncResult 단위 테스트
    └── test_orchestrator.py        # SyncOrchestrator 단위 테스트 (mock)
```

- [x] `test_dependency.py`: resolve() 결과 검증 (11개 entity × 정확한 순서)
- [x] `test_dependency.py`: resolve_all() 결과 검증
- [x] `test_dependency.py`: 사이클 없음 검증
- [x] `test_sync_context.py`: SyncResult 집계 로직 검증
- [x] `test_orchestrator.py`: mock SyncTask로 실행 순서 검증
- [x] `test_orchestrator.py`: 에러 핸들링 (개별 실패 → 종속 스킵) 검증

### 8.2 통합 테스트 (선택)

```bash
# 실제 API 호출 → DB 반영 확인 (CI에서는 skip)
# 환경변수 INTEGRATION_TEST=1 설정 시에만 실행

tests/
└── syncer/
    └── test_integration.py         # 실제 sync 실행 검증
```

- [ ] `competition` sync → DB에 competition 존재 확인
- [ ] `team --competition-id 1 --season-id 578` sync → DB에 team 존재 확인
- [ ] `all --competition-id 1 --season-id 578` sync → 전체 데이터 갱신 확인

### 8.3 CLI 검증

```bash
# 1. help 출력
python app.py sync --help

# 2. 입력 검증 확인
python app.py sync team                           # Error: --competition-id required
python app.py sync team --competition-id 1        # Error: --season-id required

# 3. 실행 확인
python app.py sync competition
python app.py sync team --competition-id 1 --season-id 578

# 4. 결과 테이블 확인
# ┌─────────────┬─────────┬─────────┬─────────┬────────┐
# │ Entity      │ Created │ Updated │ Skipped │ Errors │
# ...
```

### 8.4 체크리스트

- [x] pytest 단위 테스트 전체 통과
- [x] import 검증: `from football_data_manager.syncer.orchestrator import SyncOrchestrator`
- [x] CLI 검증: `python app.py sync --help` 정상 출력
- [x] 입력 검증: 필수 파라미터 누락 시 에러 메시지 출력
- [x] `__init__.py` 파일 모두 비어 있음 확인

---

## 9. 검증 체크리스트

### Import 검증

```bash
python -c "
from football_data_manager.syncer.dependency import SyncEntity, DependencyResolver, DEPENDENCY_GRAPH
from football_data_manager.syncer.orchestrator import SyncOrchestrator
from football_data_manager.syncer.container import SyncContainer
from football_data_manager.syncer.tasks.base import AbstractSyncTask, SyncResult, SyncContext
from football_data_manager.syncer.tasks.competition import CompetitionSyncTask
from football_data_manager.syncer.tasks.season import SeasonSyncTask
from football_data_manager.syncer.tasks.team import TeamSyncTask
from football_data_manager.syncer.tasks.player import PlayerSyncTask
from football_data_manager.syncer.tasks.fixture import FixtureSyncTask
from football_data_manager.syncer.tasks.match import MatchSyncTask
from football_data_manager.syncer.tasks.match_stat import MatchStatSyncTask
from football_data_manager.syncer.tasks.player_stat import PlayerStatSyncTask
from football_data_manager.syncer.tasks.team_stat import TeamStatSyncTask
from football_data_manager.syncer.tasks.award import AwardSyncTask
from football_data_manager.syncer.tasks.news import NewsSyncTask
print('All syncer imports OK')
"
```

### __init__.py 검증

```bash
wc -l football_data_manager/syncer/__init__.py football_data_manager/syncer/tasks/__init__.py
# 0 lines each
```

### 종속성 그래프 검증

```bash
python -c "
from football_data_manager.syncer.dependency import DependencyResolver, SyncEntity
for entity in SyncEntity:
    chain = DependencyResolver.resolve(entity)
    print(f'{entity.value:15s} → {[e.value for e in chain]}')
"
```

예상 출력:

```
competition     → ['competition']
season          → ['competition', 'season']
team            → ['competition', 'season', 'team']
player          → ['competition', 'season', 'team', 'player']
fixture         → ['competition', 'season', 'team', 'fixture']
match           → ['competition', 'season', 'team', 'player', 'fixture', 'match']
match-stat      → ['competition', 'season', 'team', 'player', 'fixture', 'match', 'match-stat']
player-stat     → ['competition', 'season', 'team', 'player', 'player-stat']
team-stat       → ['competition', 'season', 'team', 'player', 'fixture', 'match', 'team-stat']
award           → ['competition', 'season', 'team', 'player', 'fixture', 'match', 'player-stat', 'award']
news            → ['news']
```

---

## 10. Phase 4 완료 기준

- [x] `syncer/` 디렉토리 구조 완성 (15파일 + 2 `__init__.py`)
- [x] `DependencyResolver`: 11개 entity 종속성 해결, 단위 테스트 통과
- [x] `SyncOrchestrator`: 종속성 순서대로 SyncTask 실행, 결과 집계, 메모리 로깅
- [x] 11개 `SyncTask`: 각 entity별 Pull → Merge 파이프라인 구현
- [ ] **메모리 관리**: SyncTask별 독립 세션 스코핑 적용
- [x] **배치 처리**: 대량 SyncTask (Player, Fixture, Match, MatchStat, PlayerStat)에 배치 처리 적용
- [x] **SyncContext 경량화**: ID 기반 구현, Entity 전체 참조 없음
- [x] **메모리 모니터링**: SyncTask 전후 RSS 로깅, 결과 테이블에 메모리 컬럼 포함
- [x] `app.py sync` 명령어: CLI에서 entity + 옵션 입력 후 실행 가능
- [x] 입력 검증: 필수 파라미터 누락 시 에러 메시지 출력
- [x] 결과 요약: 실행 후 Entity별 Created/Updated/Skipped/Errors/Memory 테이블 출력
- [ ] 에러 핸들링: 개별 entity 실패 시 종속 entity 스킵 + 나머지 계속 진행 + 세션 자동 rollback
- [x] `__init__.py` 파일 모두 비어 있음
- [x] `psutil` 의존성 추가 (pyproject.toml)
- [x] pytest 단위 테스트 전체 통과
- [ ] 통합 테스트: PL 1시즌 full sync 시 피크 메모리 < 100 MB 확인

---

## 11. 다음 단계

Phase 4 완료 후:

1. **Phase 5: Data Validator 구현** → `app.py validate` 명령어 추가, 데이터 교차 검증
2. **Phase 6: Scheduler 구현** → APScheduler 기반 자동 실행
3. **기존 `pull-data` 명령어 정리** → `sync`로 대체 후 deprecated 처리
4. **`run` 명령어 연결** → Scheduler가 SyncOrchestrator를 호출하는 구조

---

**Last Updated**: 2026-02-23
**Maintained By**: @jormal
