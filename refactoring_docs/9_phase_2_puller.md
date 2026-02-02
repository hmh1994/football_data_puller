# Phase 2: Puller 리팩토링

**상태**: 완료 ✅
**목표**: Puller 컴포넌트 전면 재구성 (Interface + Client + Puller + Container)
**선행 조건**: Phase 1 완료 ✅

> **시작 전에**: 이 문서는 실행 가이드입니다. 전체 계획은 `1_master_plan.md`를 참고하세요.

---

## 목차

1. [개요](#1-개요)
2. [Step 1: 디렉토리 구조 생성](#2-step-1-디렉토리-구조-생성)
3. [Step 2: CamelCaseModel 기반 클래스 마이그레이션](#3-step-2-camelcasemodel-기반-클래스-마이그레이션)
4. [Step 3: Pulselive Interface 마이그레이션](#4-step-3-pulselive-interface-마이그레이션)
5. [Step 4: The Athletic Interface 마이그레이션](#5-step-4-the-athletic-interface-마이그레이션)
6. [Step 5: HTTP Client 구현 (Pulselive)](#6-step-5-http-client-구현-pulselive)
7. [Step 6: GraphQL Client 구현 (The Athletic)](#7-step-6-graphql-client-구현-the-athletic)
8. [Step 7: AbstractPuller 구현](#8-step-7-abstractpuller-구현)
9. [Step 8: Pulselive Puller 마이그레이션](#9-step-8-pulselive-puller-마이그레이션)
10. [Step 9: The Athletic Puller 마이그레이션](#10-step-9-the-athletic-puller-마이그레이션)
11. [Step 10: PullerContainer 구현](#11-step-10-pullercontainer-구현)
12. [Step 11: 검증](#12-step-11-검증)
13. [검증 체크리스트](#13-검증-체크리스트)
14. [Phase 2 완료 기준](#14-phase-2-완료-기준)
15. [다음 단계](#15-다음-단계)

---

## 1. 개요

### 1.1 Phase 2 범위

Phase 2는 Puller 컴포넌트를 전면 재구성하는 단계입니다:

- **Interface 마이그레이션**: 현재 `archive/.../models/responses/` → 새로운 `puller/interfaces/`
- **Client 분리**: WebClient/GraphQL 클라이언트를 독립 모듈로 분리
- **AbstractPuller 구현**: 타입 안전한 Puller 추상 클래스
- **개별 Puller 재구현**: archive 참조하여 비즈니스 로직 보존
- **DI Container**: `PullerContainer` 재구현

### 1.2 현재 상태 (Phase 1 완료 후)

```
football_data_manager/
├── repository/                   # ✅ Phase 1 완료
│   ├── entities/                 # 15 Entity + 11 Association (개별 파일)
│   ├── repositories/             # 15 Repository + base + pulselive
│   ├── session.py                # SessionFactory
│   └── container.py              # RepositoryContainer (17 providers)
├── common/
│   ├── enums/                    # 8개 Enum ✅ 유지
│   ├── services/
│   │   ├── config/               # ConfigService ✅ 유지
│   │   └── db/                   # 비어있음
│   └── utils/                    # Pydantic helpers, type helpers ✅ 유지
├── migrations/                   # Alembic ✅ 유지
└── puller/                       # ❌ 아직 없음 (archive에만 존재)
```

### 1.3 Phase 2 완료 후 목표 구조

```
football_data_manager/
├── repository/                   # Phase 1 완료 ✅
│   └── ...
├── puller/                       # ★ 새로 생성
│   ├── __init__.py
│   ├── interfaces/               # Pydantic 응답 모델 (TypedDict + BaseModel)
│   │   ├── __init__.py
│   │   ├── base.py               # CamelCaseModel, RawResponseModel
│   │   ├── pulselive/            # Pulselive API 응답 모델 (API 버전별 분리)
│   │   │   ├── __init__.py
│   │   │   ├── _types.py          # 공통 TypedDict (PersonDict, CountryDict 등)
│   │   │   ├── v1_award.py        # v1 Award 응답 모델
│   │   │   ├── v1_competition.py  # v1 Competition 응답 모델
│   │   │   ├── v1_match.py        # v1 Match event, officials, stat, fixture 응답 모델
│   │   │   ├── v1_player.py       # v1 Player 응답 모델
│   │   │   ├── v1_team.py         # v1 Team 응답 모델
│   │   │   ├── v2_match.py        # v2 Match detail, v3 lineup 응답 모델
│   │   │   ├── v2_player.py       # v2 Squad, player stat 응답 모델
│   │   │   └── v2_team_stat.py    # v2 Team stat 응답 모델
│   │   └── the_athletic/         # The Athletic GraphQL 응답 모델
│   │       ├── __init__.py
│   │       ├── _types.py          # 공통 TypedDict (AuthorDict)
│   │       ├── league_feed.py     # LeagueFeedResponse, QueryVariables
│   │       └── news.py           # ArticleResponse, NewsTranslateResponse
│   ├── clients/                  # HTTP/GraphQL 클라이언트
│   │   ├── __init__.py
│   │   ├── base.py               # AbstractWebClient (httpx 기반)
│   │   ├── pulselive.py          # PulseliveClient
│   │   └── the_athletic.py       # TheAthleticClient (GraphQL)
│   ├── pullers/                  # Puller 구현체
│   │   ├── __init__.py
│   │   ├── base.py               # AbstractPuller
│   │   ├── pulselive/            # Pulselive Puller 구현
│   │   │   ├── __init__.py
│   │   │   ├── award.py          # AwardPuller
│   │   │   ├── competition.py    # CompetitionPuller
│   │   │   ├── fixture.py        # FixturePuller
│   │   │   ├── match.py          # MatchPuller
│   │   │   ├── match_stat.py     # MatchStatPuller
│   │   │   ├── player.py         # PlayerPuller
│   │   │   ├── player_stat.py    # PlayerStatPuller
│   │   │   ├── season.py         # SeasonPuller
│   │   │   ├── team.py           # TeamPuller
│   │   │   └── team_stat.py      # TeamStatPuller
│   │   └── the_athletic/         # The Athletic Puller 구현
│   │       ├── __init__.py
│   │       └── news.py           # NewsPuller
│   └── container.py              # PullerContainer (DI)
├── common/                       # 공유 유틸리티 ✅ 유지
│   └── ...
└── migrations/                   # Alembic ✅ 유지
```

### 1.4 파일 수 요약

| 디렉토리 | 파일 수 | 설명 |
|---------|--------|------|
| `interfaces/` | 14 | 응답 모델 (archive 50+ → API 버전별 통합, `_types.py` 공통 분리) |
| `clients/` | 3 | base + pulselive + the_athletic |
| `pullers/` | 12 | base + 10 pulselive + 1 the_athletic |
| `container.py` | 1 | DI Container |
| **합계** | **30** | (`__init__.py` 8개 제외) |

### 1.5 핵심 설계 결정

| 항목 | 결정 | 이유 |
|------|------|------|
| **응답 모델 통합** | API 버전별 파일로 통합 (50 → 8+3) | API 버전 구분 명확, 관련 모델 그룹핑 |
| **공통 TypedDict 분리** | `_types.py`로 공통 TypedDict 분리 | 여러 버전 파일에서 공유, 중복 제거 |
| **Base 모델 이원화** | `CamelCaseModel` + `RawResponseModel` | API 원본 키 유지(`RawResponseModel`), camelCase 변환 필요 시(`CamelCaseModel`) |
| **TypedDict vs BaseModel** | Top-level: BaseModel, Nested: TypedDict | 성능 최적화 (master_plan 4.2.1) |
| **Legacy Pulselive** | 참조용 보존, 마이그레이션 안 함 | 기능 중복, pulselive_new가 주력 |
| **Client 분리** | 독립 모듈 (`clients/`) | 테스트 용이, 관심사 분리 |
| **네이밍** | 접두사 제거 (`PulseliveNew` → 도메인별) | 디렉토리가 네임스페이스 역할 |

### 1.6 Archive 참조 경로

| 대상 | Archive 경로 |
|------|-------------|
| Pulselive WebClient | `archive/.../puller/services/pulselive_new/components/pulselive_new_webclient.py` |
| Pulselive Pullers (10) | `archive/.../puller/services/pulselive_new/services/pulselive_new_*_puller.py` |
| Pulselive Models (50) | `archive/.../puller/services/pulselive_new/models/responses/` |
| The Athletic Service | `archive/.../puller/services/the_athletic/services/the_athletic_graphql_service.py` |
| The Athletic Puller | `archive/.../puller/services/the_athletic/the_athletic_puller_service.py` |
| The Athletic Models (11) | `archive/.../puller/services/the_athletic/models/` |
| Base Web Client | `archive/.../common/services/client/web_client_service.py` |
| Base GraphQL Client | `archive/.../common/services/client/graphql_client_service.py` |
| CamelCaseModel | `archive/.../common/utils/pydantic_helper/camelcase_model.py` |
| DI Container | `archive/.../puller/services/puller_service_container.py` |
| Translator Service | `archive/.../common/services/translator/translatorService.py` |
| Resource Client | `archive/.../common/services/client/resource_validation_client.py` |

---

## 2. Step 1: 디렉토리 구조 생성

- [x] **완료**

### 2.1 실행

```bash
# puller 디렉토리 구조 생성
mkdir -p football_data_manager/puller/{interfaces/{pulselive,the_athletic},clients,pullers/{pulselive,the_athletic}}

# 빈 __init__.py 생성
touch football_data_manager/puller/__init__.py
touch football_data_manager/puller/interfaces/__init__.py
touch football_data_manager/puller/interfaces/pulselive/__init__.py
touch football_data_manager/puller/interfaces/the_athletic/__init__.py
touch football_data_manager/puller/clients/__init__.py
touch football_data_manager/puller/pullers/__init__.py
touch football_data_manager/puller/pullers/pulselive/__init__.py
touch football_data_manager/puller/pullers/the_athletic/__init__.py
```

### 2.2 검증

```bash
# 구조 확인
find football_data_manager/puller -type f | sort
```

예상 출력:
```
football_data_manager/puller/__init__.py
football_data_manager/puller/clients/__init__.py
football_data_manager/puller/interfaces/__init__.py
football_data_manager/puller/interfaces/pulselive/__init__.py
football_data_manager/puller/interfaces/the_athletic/__init__.py
football_data_manager/puller/pullers/__init__.py
football_data_manager/puller/pullers/pulselive/__init__.py
football_data_manager/puller/pullers/the_athletic/__init__.py
```

---

## 3. Step 2: CamelCaseModel 기반 클래스 마이그레이션

- [x] **완료**

### 3.1 목적

모든 Pulselive 응답 모델의 기반이 되는 `CamelCaseModel`을 `puller/interfaces/base.py`로 마이그레이션합니다.

### 3.2 Archive 참조

- `archive/.../common/utils/pydantic_helper/camelcase_model.py`

### 3.3 구현

```python
# puller/interfaces/base.py
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """camelCase JSON 필드를 snake_case Python 필드로 매핑하는 기본 모델.

    Phase 3 Merger 등 다른 모듈의 중간 모델에서 활용할 수 있도록 유지합니다.
    puller/interfaces에서는 사용하지 않습니다.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        extra="ignore",
        populate_by_name=True,
        strict=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
    )


class RawResponseModel(BaseModel):
    """외부 API 응답을 원형 그대로 수신하는 기본 모델.

    alias_generator 없이 API JSON 키 이름을 필드명으로 직접 사용합니다.
    puller/interfaces의 모든 외부 API 응답 모델이 이 클래스를 상속합니다.
    """

    model_config = ConfigDict(
        extra="ignore",
        str_strip_whitespace=True,
    )
```

### 3.4 설계 변경 (계획 → 구현)

- **계획**: `CamelCaseModel`을 모든 응답 모델의 기반으로 사용
- **구현**: `RawResponseModel`을 새로 추가하여 응답 모델 기반으로 사용
- **이유**: Pulselive API 응답은 camelCase와 snake_case가 혼재 (예: match stat은 snake_case). `alias_generator`를 적용하면 snake_case 필드를 인식하지 못하는 문제 발생. `RawResponseModel`은 alias 변환 없이 API 원본 키를 직접 필드명으로 사용하여 모든 응답 형식을 처리
- `CamelCaseModel`은 Phase 3 Merger 등 다른 모듈에서 활용 가능하도록 유지

### 3.5 참고

- 기존 `common/utils/pydantic_helper/camelcase_model.py`는 유지 (다른 곳에서 참조 가능)
- Puller 컴포넌트 내에서는 `puller/interfaces/base.py`의 것을 사용

---

## 4. Step 3: Pulselive Interface 마이그레이션

- [x] **완료**

### 4.1 목적

archive의 50개 응답 모델 파일을 도메인별로 통합하여 ~12개 파일로 재구성합니다.

### 4.2 파일 매핑 (Archive → New)

> **구현 시 변경**: 계획에서는 도메인별 파일(award.py 등)로 통합했으나, 구현에서는 **API 버전별** (`v1_*`, `v2_*`)로 분리하고 공통 TypedDict를 `_types.py`로 추출했습니다. API 버전 구분이 더 명확하고, 한 파일에 같은 엔드포인트 버전의 모델이 모여 응집도가 높아집니다.

| 새 파일 | Archive 소스 파일 | 주요 클래스 |
|---------|-----------------|------------|
| `_types.py` | 공통 추출 | PersonDict, CountryDict, StadiumDict, MatchTeamDict, PaginatedDict |
| `v1_award.py` | `pulselive_new_award_*.py`, `pulselive_new_v1_award_response.py` | AwardTeamDict, PlayerAwardDict, ManagerAwardDict, V1AwardResponse |
| `v1_competition.py` | `pulselive_new_competition_*.py`, `pulselive_new_v1_competition_*.py` | CompetitionItemDict, V1CompetitionResponse, V1CompetitionDetailResponse |
| `v1_match.py` | `pulselive_new_match_response.py`, `pulselive_new_v1_matchweek_*.py`, `pulselive_new_event_*.py`, `pulselive_new_v1_event_response.py`, `pulselive_new_v1_match_officials_response.py`, `pulselive_new_match_stat_info_response.py`, `pulselive_new_v1_match_team_stat_response.py` | MatchDict, V1MatchweekMatchesResponse, EventCardDict, EventGoalDict, EventSubDict, V1EventResponse, V1MatchOfficialsResponse, MatchStatInfoResponse, V1MatchTeamStatResponse |
| `v1_player.py` | `pulselive_new_player_*.py`, `pulselive_new_v1_player_*.py` | PlayerResponse, PlayerDatesResponse, PlayerDetailResponse, V1PlayerDetailsResponse, V1PlayerResponse |
| `v1_team.py` | `pulselive_new_team_response.py`, `pulselive_new_v1_teams_response.py` | TeamItemDict, V1TeamsResponse |
| `v2_match.py` | `pulselive_new_v2_match_response.py`, `pulselive_new_v3_match_lineup_response.py` | V2MatchResponse, PlayerSimpleDict, TeamLineupDict, V3MatchLineupResponse |
| `v2_player.py` | `pulselive_new_v2_squad_response.py`, `pulselive_new_player_stats_response.py`, `pulselive_new_v2_player_stat_response.py` | V2SquadResponse, PlayerStatsDict, V2PlayerStatResponse |
| `v2_team_stat.py` | `pulselive_new_team_stats_response.py`, `pulselive_new_v2_team_stats_response.py` | TeamStatsDict, V2TeamStatsResponse |

### 4.3 설계 원칙

1. **관련 모델 그룹핑**: 한 Puller가 사용하는 모델들은 같은 파일에 배치
2. **네이밍 정리**: `PulseliveNew` 접두사 제거 → 디렉토리가 네임스페이스 역할
3. **TypedDict 적용**: 중첩 모델은 TypedDict로 전환 (master_plan 4.2.1)
4. **기존 클래스 구조 보존**: 필드명, 타입, validator 로직 동일 유지
5. **import 경로만 변경**: 기능 변경 없이 위치만 이동

### 4.4 TypedDict 적용 기준

```python
# ✅ TypedDict로 전환 (중첩 모델, 검증 불필요)
class PlayerNameDict(TypedDict):
    simple_name: str
    full_name: str

class PlayerCountryDict(TypedDict):
    country: str
    iso_code: str | None

# ✅ BaseModel 유지 (top-level, 검증 필요)
class PlayerDetailResponse(CamelCaseModel):
    id: PlayerIdDict
    name: PlayerNameDict
    country: PlayerCountryDict
    position: str
```

### 4.5 주의사항

- `@field_validator`가 있는 모델은 **BaseModel 유지** (TypedDict는 validator 미지원)
- 예: `PlayerDetailResponse.parse_id()`, `PlayerDatesResponse.parse_birth_date()`
- `model_validate()` 호출 대상 모델은 반드시 **BaseModel**

---

## 5. Step 4: The Athletic Interface 마이그레이션

- [x] **완료**

### 5.1 파일 매핑

| 새 파일 | Archive 소스 파일 | 주요 클래스 |
|---------|-----------------|------------|
| `_types.py` | 공통 추출 | AuthorDict |
| `league_feed.py` | `the_athletic_league_feed_*.py`, `the_athletic_query_variables.py` | LeagueFeedContentDict, LeagueFeedLayoutDict, LeagueFeedMulliganDict, LeagueFeedResponse, QueryVariables |
| `news.py` | `the_athletic_article_*.py`, `news_translate_*.py` | ArticleResponse, NewsTranslateResponse |

### 5.2 구현 시 변경

- **`query.py` 병합**: `QueryVariables`는 `league_feed.py`에 포함 (LeagueFeedResponse와 함께 사용되므로 응집도 향상)
- **`_types.py` 추가**: 공통 TypedDict(`AuthorDict`)를 별도 파일로 분리
- The Athletic 모델은 GraphQL 응답 구조를 따르며 `RawResponseModel`을 상속 (snake_case 키 사용)
- **`__typename` 미포함**: GraphQL의 `__typename` 필드는 Python TypedDict의 name mangling (`__`→`_Class__`) 문제가 있어 TypedDict에서 제외. API 응답에 포함되어도 TypedDict가 extra key를 무시하므로 정상 동작

---

## 6. Step 5: HTTP Client 구현 (Pulselive)

- [x] **완료**

### 6.1 Archive 참조

- Base: `archive/.../common/services/client/web_client_service.py` → `AbstractWebClientService`
- Impl: `archive/.../puller/services/pulselive_new/components/pulselive_new_webclient.py`

### 6.2 구현 (clients/base.py)

```python
# puller/clients/base.py
from httpx import AsyncClient, URL, Timeout


class AbstractWebClient:
    """비동기 HTTP 클라이언트 기본 클래스.

    httpx AsyncClient를 래핑하여 GET/POST 요청을 제공합니다.
    """

    def __init__(self, base_url: str, timeout: float = 10.0):
        self._base_url = URL(base_url)
        self._timeout = Timeout(timeout)
        self._client = AsyncClient(base_url=self._base_url, timeout=self._timeout)

    async def get(
        self,
        path: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> dict | None:
        response = await self._client.get(path, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    async def post(
        self,
        path: str,
        params: dict | None = None,
        data: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        response = await self._client.post(
            path, params=params, data=data, json=json, headers=headers,
        )
        response.raise_for_status()
        return response.json()

    async def close(self) -> None:
        await self._client.aclose()
```

### 6.3 구현 (clients/pulselive.py)

```python
# puller/clients/pulselive.py
from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.puller.clients.base import AbstractWebClient
from football_data_manager.puller.interfaces.pulselive.competition import (
    V1CompetitionResponse,
    # ... 필요한 응답 모델
)


class PulseliveClient(AbstractWebClient):
    """Pulselive API 전용 HTTP 클라이언트.

    v1/v2/v3 엔드포인트별 메서드를 제공합니다.
    """

    def __init__(self, config: ApiConfig):
        super().__init__(base_url=config.url.unicode_string())

    # --- v1 endpoints ---

    async def get_v1_competitions(
        self, limit: int = 10, _next: str | None = None,
    ) -> V1CompetitionResponse:
        params = {"_limit": str(limit)}
        if _next:
            params["_next"] = _next
        response = await self.get(path="v1/competitions", params=params)
        return V1CompetitionResponse.model_validate(response)

    # ... archive의 webclient 메서드를 순서대로 마이그레이션
    # 각 메서드: params 구성 → self.get() → model_validate() → return
```

### 6.4 마이그레이션 포인트

- `PulseliveNewWebclient` → `PulseliveClient` (접두사 정리)
- `AbstractWebClientService` → `AbstractWebClient` (Service 접미사 제거)
- `httpx.URL` → `str` (타입 단순화, URL 생성은 내부에서)
- archive의 모든 API 메서드 보존 (v1, v2, v3 엔드포인트)

---

## 7. Step 6: GraphQL Client 구현 (The Athletic)

- [x] **완료**

### 7.1 Archive 참조

- Base: `archive/.../common/services/client/graphql_client_service.py` → `AbstractGraphQLClientService`
- Impl: `archive/.../puller/services/the_athletic/services/the_athletic_graphql_service.py`

### 7.2 구현 (clients/the_athletic.py)

```python
# puller/clients/the_athletic.py
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from football_data_manager.common.services.config.models.api_config import ApiConfig
from football_data_manager.puller.interfaces.the_athletic.news import (
    LeagueFeedResponse,
)
from football_data_manager.puller.interfaces.the_athletic.query import QueryVariables


class TheAthleticClient:
    """The Athletic GraphQL API 클라이언트.

    gql 라이브러리를 사용하여 GraphQL 쿼리를 실행합니다.
    """

    _LEAGUE_IDS = {"EN_PR": 6}

    _LEAGUE_FEED_QUERY = """
    query LeagueFeedQuery($feed: String!, $feed_id: Int!, $page: Int!) {
        feedMulligan(feed: $feed, feed_id: $feed_id, page: $page) {
            __typename
            layouts {
                __typename
                type
                typename
                contents {
                    __typename
                    ... on ArticleConsumable {
                        title
                        consumable_id
                        author { first_name last_name }
                        excerpt
                        image_uri
                        permalink
                    }
                }
            }
        }
    }
    """

    def __init__(self, config: ApiConfig):
        self._transport = AIOHTTPTransport(
            url=config.url.unicode_string(),
            timeout=10,
        )
        self._client = Client(
            transport=self._transport,
            fetch_schema_from_transport=False,
        )

    async def get_league_feed(
        self, league_abbr: str, page: int,
    ) -> LeagueFeedResponse:
        variables = QueryVariables(
            feed="league",
            feed_id=self._LEAGUE_IDS[league_abbr],
            page=page,
        )
        result = await self._execute(
            query=self._LEAGUE_FEED_QUERY,
            variables=variables.model_dump(),
            operation_name="LeagueFeedQuery",
        )
        return LeagueFeedResponse.model_validate(result)

    async def _execute(
        self,
        query: str,
        variables: dict | None = None,
        operation_name: str | None = None,
    ) -> dict:
        document = gql(query)
        async with self._client as session:
            return await session.execute(
                document,
                variable_values=variables,
                operation_name=operation_name,
            )

    async def close(self) -> None:
        await self._transport.close()
```

### 7.3 마이그레이션 포인트

- `TheAthleticGraphQLService` → `TheAthleticClient` (명확한 역할명)
- `AbstractGraphQLClientService` 상속 제거 → 직접 구현 (단일 구현체이므로)
- GraphQL 쿼리 문자열은 클래스 상수로 유지

---

## 8. Step 7: AbstractPuller 구현

- [x] **완료**

### 8.1 설계

```python
# puller/pullers/base.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic

from pydantic import BaseModel

TResponse = TypeVar("TResponse", bound=BaseModel)


class AbstractPuller(ABC, Generic[TResponse]):
    """모든 Puller의 추상 베이스 클래스.

    데이터 소스에서 데이터를 가져와 Pydantic 응답 모델로 반환합니다.
    Puller는 데이터 수집만 담당하며, Entity 변환은 Merger(Phase 3)에서 처리합니다.
    """

    @abstractmethod
    async def close(self) -> None:
        """클라이언트 리소스를 정리합니다."""
        ...
```

### 8.2 설계 결정

| 항목 | 결정 | 이유 |
|------|------|------|
| `pull()` 추상 메서드 | 정의하지 않음 | 각 Puller의 시그니처가 다름 (파라미터 상이) |
| `close()` 추상 메서드 | 정의 | 모든 Puller가 리소스 정리 필요 |
| Generic[TResponse] | 유지 | 타입 안전성, IDE 지원 |
| Entity 변환 | Puller에서 제거 | Phase 3 Merger로 이동 예정 |

### 8.3 Puller 역할 범위 (중요)

**Phase 2에서 Puller가 하는 일**:
1. Client를 통해 외부 API 호출
2. 응답을 Pydantic 모델로 파싱
3. 반환 (Entity 변환 없음)

**Phase 3에서 Merger가 할 일**:
1. Puller 응답을 받아 Entity로 변환
2. Repository를 통해 DB에 저장
3. 번역, 캐싱 등 비즈니스 로직 처리

> ⚠️ **주의**: archive의 Puller는 Entity 생성/저장까지 직접 수행합니다.
> Phase 2에서는 **API 호출 + 응답 파싱**만 마이그레이션하고,
> Entity 변환 로직은 Phase 3 Merger로 분리합니다.

---

## 9. Step 8: Pulselive Puller 마이그레이션

- [x] **완료**

### 9.1 Puller 목록 (10개)

| 새 파일 | Archive 소스 | 역할 |
|---------|-------------|------|
| `pullers/pulselive/award.py` | `pulselive_new_award_puller.py` | 시상 정보 수집 |
| `pullers/pulselive/competition.py` | `pulselive_new_competition_puller.py` | 대회 정보 수집 |
| `pullers/pulselive/fixture.py` | `pulselive_new_fixture_puller.py` | 경기 일정 수집 |
| `pullers/pulselive/match.py` | `pulselive_new_match_puller.py` | 경기 상세 수집 |
| `pullers/pulselive/match_stat.py` | `pulselive_new_match_stat_puller.py` | 경기 통계 수집 |
| `pullers/pulselive/player.py` | `pulselive_new_player_puller.py` | 선수 정보 수집 |
| `pullers/pulselive/player_stat.py` | `pulselive_new_player_stats_puller.py` | 선수 통계 수집 |
| `pullers/pulselive/season.py` | `pulselive_new_season_puller.py` | 시즌 정보 수집 |
| `pullers/pulselive/team.py` | `pulselive_new_team_puller.py` | 팀 정보 수집 |
| `pullers/pulselive/team_stat.py` | `pulselive_new_team_stats_puller.py` | 팀 통계 수집 |

### 9.2 마이그레이션 패턴

각 Puller는 다음 패턴으로 재구성합니다:

```python
# puller/pullers/pulselive/player.py
from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.interfaces.pulselive.player import (
    V2SquadResponse,
    PlayerDetailResponse,
)
from football_data_manager.puller.pullers.base import AbstractPuller


class PlayerPuller(AbstractPuller[PlayerDetailResponse]):
    """Pulselive API에서 선수 데이터를 수집합니다."""

    def __init__(self, client: PulseliveClient):
        self._client = client

    async def pull_squad(
        self,
        competition_source_id: str,
        season_source_id: str,
        team_source_id: str,
    ) -> V2SquadResponse:
        """팀 스쿼드 (선수 목록)를 수집합니다."""
        return await self._client.get_v2_squad(
            competition_source_id, season_source_id, team_source_id,
        )

    async def close(self) -> None:
        await self._client.close()
```

### 9.3 마이그레이션 핵심 변경사항

1. **의존성 단순화**: Repository, Translator, ResourceClient 제거 → Client만 주입
2. **Entity 변환 로직 제거**: `process_player()`, `_create_new()`, `_update_existing()` → Phase 3
3. **캐싱 로직 제거**: `__country_translation_cache` → Phase 3 Merger
4. **순수 API 호출만 유지**: Client 호출 → 응답 반환
5. **네이밍 정리**: `PulseliveNewPlayerPuller` → `PlayerPuller`

### 9.4 의존성 관계 변화

```
# Archive (현재)
Puller → WebClient + Repository + Translator + ResourceClient
  └─ Entity 생성/수정/저장까지 직접 처리

# Phase 2 (목표)
Puller → Client
  └─ API 호출 + 응답 파싱만 처리

# Phase 3 (예정)
Merger → Puller + Repository + Translator
  └─ 응답 → Entity 변환 + DB 저장
```

---

## 10. Step 9: The Athletic Puller 마이그레이션

- [x] **완료**

### 10.1 Archive 참조

- `archive/.../puller/services/the_athletic/the_athletic_puller_service.py`

### 10.2 구현

```python
# puller/pullers/the_athletic/news.py
from football_data_manager.puller.clients.the_athletic import TheAthleticClient
from football_data_manager.puller.interfaces.the_athletic.news import (
    LeagueFeedResponse,
)
from football_data_manager.puller.pullers.base import AbstractPuller


class NewsPuller(AbstractPuller[LeagueFeedResponse]):
    """The Athletic에서 뉴스 데이터를 수집합니다."""

    def __init__(self, client: TheAthleticClient):
        self._client = client

    async def pull_league_feed(
        self, league_abbr: str, page: int = 1,
    ) -> LeagueFeedResponse:
        """리그별 뉴스 피드를 수집합니다."""
        return await self._client.get_league_feed(league_abbr, page)

    async def close(self) -> None:
        await self._client.close()
```

---

## 11. Step 10: PullerContainer 구현

- [x] **완료**

### 11.1 Archive 참조

- `archive/.../puller/services/puller_service_container.py`

### 11.2 구현

```python
# puller/container.py
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Singleton, Factory

from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.clients.the_athletic import TheAthleticClient
from football_data_manager.puller.pullers.pulselive.award import AwardPuller
from football_data_manager.puller.pullers.pulselive.competition import CompetitionPuller
from football_data_manager.puller.pullers.pulselive.fixture import FixturePuller
from football_data_manager.puller.pullers.pulselive.match import MatchPuller
from football_data_manager.puller.pullers.pulselive.match_stat import MatchStatPuller
from football_data_manager.puller.pullers.pulselive.player import PlayerPuller
from football_data_manager.puller.pullers.pulselive.player_stat import PlayerStatPuller
from football_data_manager.puller.pullers.pulselive.season import SeasonPuller
from football_data_manager.puller.pullers.pulselive.team import TeamPuller
from football_data_manager.puller.pullers.pulselive.team_stat import TeamStatPuller
from football_data_manager.puller.pullers.the_athletic.news import NewsPuller


class PullerContainer(DeclarativeContainer):
    """Puller 컴포넌트 DI 컨테이너.

    Clients, Pullers를 관리합니다.
    """

    config = Configuration()

    # --- Clients ---

    pulselive_client = Singleton(
        PulseliveClient,
        config=config.pulselive,
    )

    the_athletic_client = Singleton(
        TheAthleticClient,
        config=config.the_athletic,
    )

    # --- Pulselive Pullers ---

    award_puller = Factory(AwardPuller, client=pulselive_client)
    competition_puller = Factory(CompetitionPuller, client=pulselive_client)
    fixture_puller = Factory(FixturePuller, client=pulselive_client)
    match_puller = Factory(MatchPuller, client=pulselive_client)
    match_stat_puller = Factory(MatchStatPuller, client=pulselive_client)
    player_puller = Factory(PlayerPuller, client=pulselive_client)
    player_stat_puller = Factory(PlayerStatPuller, client=pulselive_client)
    season_puller = Factory(SeasonPuller, client=pulselive_client)
    team_puller = Factory(TeamPuller, client=pulselive_client)
    team_stat_puller = Factory(TeamStatPuller, client=pulselive_client)

    # --- The Athletic Pullers ---

    news_puller = Factory(NewsPuller, client=the_athletic_client)
```

### 11.3 설계 결정

| 항목 | 결정 | 이유 |
|------|------|------|
| Client | Singleton | HTTP 연결 재사용, 리소스 효율 |
| Puller | Factory | 경량 객체, 필요 시 생성 |
| Legacy Pulselive | 미등록 | pulselive_new만 마이그레이션 |

---

## 12. Step 11: 검증

- [x] **완료**

### 12.1 Import 검증

```python
# 모든 import가 정상 동작하는지 확인
python -c "
from football_data_manager.puller.interfaces.base import CamelCaseModel, RawResponseModel
from football_data_manager.puller.clients.base import AbstractWebClient
from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.clients.the_athletic import TheAthleticClient
from football_data_manager.puller.pullers.base import AbstractPuller
from football_data_manager.puller.pullers.pulselive.award import AwardPuller
from football_data_manager.puller.pullers.pulselive.competition import CompetitionPuller
from football_data_manager.puller.pullers.pulselive.fixture import FixturePuller
from football_data_manager.puller.pullers.pulselive.match import MatchPuller
from football_data_manager.puller.pullers.pulselive.match_stat import MatchStatPuller
from football_data_manager.puller.pullers.pulselive.player import PlayerPuller
from football_data_manager.puller.pullers.pulselive.player_stat import PlayerStatPuller
from football_data_manager.puller.pullers.pulselive.season import SeasonPuller
from football_data_manager.puller.pullers.pulselive.team import TeamPuller
from football_data_manager.puller.pullers.pulselive.team_stat import TeamStatPuller
from football_data_manager.puller.pullers.the_athletic.news import NewsPuller
from football_data_manager.puller.container import PullerContainer
print('All imports successful')
"
```

### 12.2 Interface 모델 검증

```python
# CamelCaseModel 및 RawResponseModel 동작 확인
python -c "
from football_data_manager.puller.interfaces.base import CamelCaseModel, RawResponseModel

# CamelCaseModel: camelCase JSON → snake_case Python
class TestCamel(CamelCaseModel):
    first_name: str
    last_name: str

data = {'firstName': 'Harry', 'lastName': 'Kane'}
m = TestCamel.model_validate(data)
assert m.first_name == 'Harry'
print('CamelCaseModel validation: OK')

# RawResponseModel: API 원본 키 그대로 사용
class TestRaw(RawResponseModel):
    matchId: str
    homeTeam: str

raw = TestRaw.model_validate({'matchId': '123', 'homeTeam': 'Arsenal', 'extra': 'ignored'})
assert raw.matchId == '123'
print('RawResponseModel validation: OK')
"
```

### 12.3 Container 검증

```python
# PullerContainer 초기화 확인
python -c "
from football_data_manager.puller.container import PullerContainer
container = PullerContainer()
print(f'PullerContainer providers: {len(container.providers)}')
# 기대: config(1) + clients(2) + pullers(11) = 14
"
```

### 12.4 파일 수 검증

```bash
# 전체 파일 수 확인
find football_data_manager/puller -name "*.py" -not -name "__init__.py" | wc -l
# 기대: 29개 (interfaces 14 + clients 3 + pullers 12 + container 1 = 30, _types.py 2개 포함)

# __init__.py 확인 (모두 비어 있어야 함 = 0 bytes)
find football_data_manager/puller -name "__init__.py" -exec wc -c {} \;
# 기대: 8개, 모두 0 bytes
```

---

## 13. 검증 체크리스트

### 13.1 구조 검증

- [x] `puller/` 디렉토리 구조가 목표와 일치
- [x] 모든 `__init__.py`가 비어 있음 (8개, 모두 0 bytes)
- [x] 모든 모듈 import 성공

### 13.2 Interface 검증

- [x] `CamelCaseModel` 기본 동작 확인 (camelCase ↔ snake_case)
- [x] Pulselive 응답 모델 파싱 정상 (archive 대비 동일 결과)
- [x] The Athletic 응답 모델 파싱 정상
- [x] TypedDict 적용 모델이 `model_validate()`에서 정상 동작

### 13.3 Client 검증

- [x] `AbstractWebClient` GET/POST 메서드 정상
- [x] `PulseliveClient` 인스턴스화 성공
- [x] `TheAthleticClient` 인스턴스화 성공
- [x] `close()` 호출 시 리소스 정리 정상

### 13.4 Puller 검증

- [x] 10개 Pulselive Puller 인스턴스화 성공
- [x] 1개 The Athletic Puller 인스턴스화 성공
- [x] 모든 Puller가 `AbstractPuller` 상속 확인 (11/11)
- [x] Client 메서드 호출 시그니처 확인

### 13.5 Container 검증

- [x] `PullerContainer` 인스턴스화 성공
- [x] Provider 수 일치 (14: config + 2 clients + 11 pullers)
- [x] Client는 Singleton, Puller는 Factory 확인

---

## 14. Phase 2 완료 기준

### 14.1 필수 기준

- [x] `puller/` 디렉토리 구조 완성
- [x] 모든 Pulselive 응답 모델 마이그레이션 완료 (50+ → `_types.py` + 8 파일)
- [x] 모든 The Athletic 응답 모델 마이그레이션 완료 (`_types.py` + 2 파일)
- [x] `PulseliveClient` 구현 (archive webclient 15개 메서드 전부 포함)
- [x] `TheAthleticClient` 구현
- [x] 10개 Pulselive Puller 구현
- [x] 1개 The Athletic Puller 구현
- [x] `PullerContainer` 구현 (14 providers)
- [x] 모든 import 검증 통과 (17개 클래스)

### 14.2 품질 기준

- [x] TypedDict 적용 (중첩 모델: StadiumDict, MatchTeamDict, PaginatedDict 등)
- [x] 공통 TypedDict `_types.py`로 분리 (Pulselive, The Athletic 각각)
- [x] `RawResponseModel` 도입 (API 원본 키 유지, camelCase/snake_case 혼재 대응)
- [x] 네이밍 정리 (`PulseliveNew` 접두사 제거)
- [x] API 버전별 파일 분리 (`v1_*`, `v2_*`)
- [x] archive 대비 기능 동일 (API 호출 + 파싱)
- [x] Entity 변환 로직 미포함 (Phase 3으로 분리)
- [x] GraphQL `__typename` 필드 TypedDict에서 제외 (Python name mangling 회피)

---

## 15. 다음 단계

### Phase 3: Merger 구현

Phase 2 완료 후, Puller 응답을 Entity로 변환하는 Merger를 구현합니다:

1. Merger 디렉토리 구조 생성
2. 필요한 Merger 구현 (추상화 없이 구체적 구현)
3. Puller → Merger → Repository 파이프라인 구축
4. 번역, 캐싱 등 비즈니스 로직 Merger로 이동
5. 통합 테스트

> **참고**: Phase 2의 Puller에서 제외된 Entity 변환 로직은 Phase 3 Merger에서 구현합니다.
> archive의 Puller 코드에서 `process_*`, `_create_new`, `_update_existing` 패턴을 Merger로 이전합니다.

---

## Appendix A: Legacy Pulselive 처리 방침

### A.1 현황

- `archive/.../puller/services/pulselive/` (레거시)
- 7개 서비스 + 91개 응답 모델
- `pulselive_new`와 기능 중복

### A.2 결정

- **Phase 2에서 마이그레이션하지 않음**
- `pulselive_new`가 주력 소스 (v2/v3 API 사용)
- 레거시는 archive에서 참조만 가능
- 향후 필요 시 별도 판단

### A.3 근거

- master_plan: "pulselive (레거시, 참고용 유지)"
- API 버전이 낮아 (v1) 장기적으로 deprecated 예상
- 모든 기능이 `pulselive_new`에서 커버됨

---

## Appendix B: common/services 의존성

Phase 2에서 사용하는 `common/` 의존성:

| 모듈 | 위치 | 용도 |
|------|------|------|
| `ConfigService` | `common/services/config/` | API URL, 인증 정보 |
| `ApiConfig` | `common/services/config/models/` | API 설정 모델 |

Phase 3에서 추가로 필요한 `common/` 의존성:

| 모듈 | 위치 | 용도 |
|------|------|------|
| `TranslatorService` | archive → 복원 필요 | 한글 번역 |
| `ResourceValidationClient` | archive → 복원 필요 | URL 유효성 검증 |
| `OpenAI/AnthropicClient` | archive → 복원 필요 | 번역 서비스 백엔드 |

> ⚠️ Phase 3 시작 전, Merger에서 필요한 `common/services/` 모듈을 archive에서 복원해야 합니다.

---

*문서 생성일: 2026-02-02*
*마지막 수정: 2026-02-23 (실제 구현 반영: API 버전별 파일 분리, RawResponseModel 추가, __typename 버그 수정)*
