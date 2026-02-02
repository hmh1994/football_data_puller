# Phase 2.5: Interface 구조 개선

**상태**: 대기 중 ⏳
**목표**: 외부 API 응답을 원형 그대로 보존하고, Endpoint 기반으로 직관적으로 재구성
**선행 조건**: Phase 2 완료 ✅

---

## 목차

1. [문제 분석](#1-문제-분석)
2. [설계 원칙](#2-설계-원칙)
3. [새 디렉토리 구조](#3-새-디렉토리-구조)
4. [Step 1: Base 모델 추가](#4-step-1-base-모델-추가)
5. [Step 2: 공유 TypedDict 정의](#5-step-2-공유-typeddict-정의)
6. [Step 3: Pulselive Endpoint별 파일 재구성](#6-step-3-pulselive-endpoint별-파일-재구성)
7. [Step 4: The Athletic 파일 재구성](#7-step-4-the-athletic-파일-재구성)
8. [Step 5: Client import 경로 수정](#8-step-5-client-import-경로-수정)
9. [Step 6: 검증](#9-step-6-검증)
10. [BaseModel vs TypedDict 판정 기준](#10-basemodel-vs-typeddict-판정-기준)
11. [검증 체크리스트](#11-검증-체크리스트)
12. [완료 기준](#12-완료-기준)

---

## 1. 문제 분석

### 1.1 현재 상태

| 항목 | 현황 | 문제 |
|------|------|------|
| **CamelCaseModel** | 모든 Pulselive 모델이 상속 | API 원형 키 이름이 snake_case로 변형됨 |
| **TypedDict** | 51개 중 1개만 적용 (`StadiumDict`) | master_plan 4.2.1의 TypedDict 원칙 미이행 |
| **파일 구성** | 도메인별 (player.py, team.py...) | 어떤 endpoint의 응답인지 직관적이지 않음 |
| **필드명** | `simple_name`, `full_name` (snake_case) | API 실제 키는 `simpleName`, `fullName` (camelCase) |

### 1.2 핵심 변경 방향

```
Before: API(camelCase) → CamelCaseModel(alias_generator) → Python(snake_case)
After:  API(camelCase) → Model(camelCase 그대로) → Python(camelCase)
```

---

## 2. 설계 원칙

### 2.1 원형 보존 (Raw Preservation)

API JSON 응답의 키 이름을 Python 필드명으로 그대로 사용합니다.

```python
# Before (CamelCaseModel 변형)
class PersonResponse(CamelCaseModel):
    simple_name: str       # API 키: "simpleName" → 변형됨
    full_name: str         # API 키: "fullName" → 변형됨

# After (원형 보존)
class PersonDict(TypedDict):
    simpleName: str        # API 키 그대로
    fullName: str          # API 키 그대로
```

### 2.2 TypedDict 적극 활용

| 조건 | 타입 | 이유 |
|------|------|------|
| `model_validate()` 대상 (Top-level) | `BaseModel` | Pydantic 검증 필요 |
| `@field_validator` 사용 | `BaseModel` | TypedDict는 validator 미지원 |
| 그 외 모든 중첩 모델 | `TypedDict` | 빠른 파싱, 메모리 효율 |

### 2.3 Endpoint 기반 파일 구성

파일명만 보고 어떤 API endpoint의 응답인지 알 수 있어야 합니다.

```
# Before: 도메인별
player.py      → v1/players, v1/.../players, v2/.../squad, v2/.../stats 혼재
match.py       → v2/matches, v1/.../events, v1/.../officials, v3/.../lineups 혼재

# After: Endpoint별
v1_player.py   → v1/players/{id}, v1/.../players/{id}
v2_player.py   → v2/.../squad, v2/.../players/{id}/stats
v2_match.py    → v2/matches/{id}, v3/matches/{id}/lineups
```

---

## 3. 새 디렉토리 구조

```
puller/interfaces/
├── __init__.py
├── base.py                          # CamelCaseModel (유지) + RawResponseModel (신규)
├── pulselive/
│   ├── __init__.py
│   ├── _types.py                    # 공유 TypedDict (PersonDict 등)
│   ├── v1_competition.py            # Endpoint 1,2: competitions, competition details
│   ├── v1_team.py                   # Endpoint 3: teams
│   ├── v1_award.py                  # Endpoint 4: awards
│   ├── v1_match.py                  # Endpoint 5,6,7,8: matchweek matches, events, officials, stats
│   ├── v1_player.py                 # Endpoint 9,10: player, player details
│   ├── v2_match.py                  # Endpoint 11,12: match detail, match lineup
│   ├── v2_player.py                 # Endpoint 13,14: squad, player stats
│   └── v2_team_stat.py              # Endpoint 15: team stats
└── the_athletic/
    ├── __init__.py
    ├── league_feed.py               # LeagueFeedQuery 응답
    └── news.py                      # Article, NewsTranslate 응답
```

### 3.1 파일-Endpoint 매핑 (Pulselive)

| 파일 | Client 메서드 | API Path |
|------|-------------|----------|
| `v1_competition.py` | `get_v1_competitions()` | `v1/competitions` |
| | `get_v1_competition_details()` | `v1/competitions/{id}/details` |
| `v1_team.py` | `get_v1_teams()` | `v1/.../teams` |
| `v1_award.py` | `get_v1_awards()` | `v1/.../awards` |
| `v1_match.py` | `get_v1_matchweek_matches()` | `v1/.../matchweeks/{n}/matches` |
| | `get_v1_match_event()` | `v1/matches/{id}/events` |
| | `get_v1_match_official()` | `v1/matches/{id}/officials` |
| | `get_v1_match_stat()` | `v1/matches/{id}/stats` |
| `v1_player.py` | `get_v1_player()` | `v1/players/{id}` |
| | `get_v1_player_details()` | `v1/.../players/{id}` |
| `v2_match.py` | `get_v2_match()` | `v2/matches/{id}` |
| | `get_v3_match_lineup()` | `v3/matches/{id}/lineups` |
| `v2_player.py` | `get_v2_squad()` | `v2/.../squad` |
| | `get_v2_player_stats()` | `v2/.../players/{id}/stats` |
| `v2_team_stat.py` | `get_v2_team_stats()` | `v2/.../teams/{id}/stats` |

### 3.2 파일-Endpoint 매핑 (The Athletic)

| 파일 | Client 메서드 | GraphQL Query |
|------|-------------|---------------|
| `league_feed.py` | `get_league_feed()` | `LeagueFeedQuery` |
| `news.py` | (Phase 3에서 사용) | Article, NewsTranslate |

---

## 4. Step 1: Base 모델 추가

- [ ] **완료**

### 4.1 변경 내용

`CamelCaseModel`은 **유지**하고, `RawResponseModel`을 **추가**합니다.

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

### 4.2 두 모델 병존 이유

| 모델 | 사용처 | 역할 |
|------|--------|------|
| `CamelCaseModel` | Phase 3 Merger, 내부 DTO 등 | camelCase ↔ snake_case 자동 매핑이 필요한 모델 |
| `RawResponseModel` | `puller/interfaces/*` | 외부 API 응답 원형 보존 (alias 변환 없음) |

### 4.3 RawResponseModel의 ConfigDict 설계

| 옵션 | CamelCaseModel | RawResponseModel | RawResponseModel에서의 판단 |
|------|----------------|------------------|---------------------------|
| `alias_generator=to_camel` | ✓ | 제거 | 원형 보존 원칙 |
| `populate_by_name=True` | ✓ | 제거 | alias 없으므로 불필요 |
| `strict=True` | ✓ | 제거 | TypedDict와의 혼용 시 불필요한 제약 |
| `use_enum_values=True` | ✓ | 제거 | Interface에 Enum 미사용 |
| `validate_assignment=True` | ✓ | 제거 | 읽기 전용 응답 모델 |
| `validate_default=True` | ✓ | 제거 | 기본값에 대한 추가 검증 불필요 |
| `extra="ignore"` | ✓ | 유지 | API 응답에 예상 외 필드 무시 |
| `str_strip_whitespace=True` | ✓ | 유지 | 문자열 정리 유용 |

> **참고**: CamelCaseModel의 ConfigDict 옵션은 모두 그대로 유지됩니다.
> RawResponseModel은 외부 API 응답 전용이므로 최소한의 옵션만 적용합니다.

---

## 5. Step 2: 공유 TypedDict 정의

- [ ] **완료**

### 5.1 Pulselive 공유 타입 (`pulselive/_types.py`)

여러 endpoint에서 공통으로 사용되는 TypedDict를 정의합니다.

```python
# puller/interfaces/pulselive/_types.py
from typing import TypedDict


class PersonDict(TypedDict):
    """Person name. 다수 endpoint에서 공통 사용."""
    simpleName: str
    fullName: str


class CountryDict(TypedDict):
    """Country info."""
    country: str
    isoCode: str | None
    demonym: str | None


class StadiumDict(TypedDict, total=False):
    """Stadium info (모든 필드 optional)."""
    country: str | None
    city: str | None
    name: str | None
    capacity: int | None


class MatchTeamDict(TypedDict):
    """팀 점수 정보. fixture/match에서 공통 사용."""
    score: int | None
    name: str
    id: str
    halfTimeScore: int | None
    shortName: str | None
    redCards: int | None


class PaginatedDict(TypedDict):
    """Pagination metadata. _limit, _prev, _next 키 사용."""
    _limit: int
    _prev: str | None
    _next: str | None
```

> **주의**: `PaginatedDict`의 `_limit`, `_prev`, `_next`는 API가 실제로 보내는 키입니다.
> TypedDict에서는 `_` 접두사 키를 허용하므로 그대로 사용합니다.

### 5.2 The Athletic 공유 타입 (`the_athletic/_types.py`)

The Athletic GraphQL 응답은 snake_case를 사용합니다.

```python
# puller/interfaces/the_athletic/_types.py
from typing import TypedDict


class AuthorDict(TypedDict):
    """Author info. league_feed, article에서 공통 사용."""
    first_name: str
    last_name: str
```

---

## 6. Step 3: Pulselive Endpoint별 파일 재구성

- [ ] **완료**

### 6.1 `v1_competition.py`

**Endpoint**: `v1/competitions`, `v1/competitions/{id}/details`

```python
# puller/interfaces/pulselive/v1_competition.py
from typing import TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import PaginatedDict


class CompetitionItemDict(TypedDict):
    code: str
    name: str
    id: str


class V1CompetitionResponse(RawResponseModel):
    """GET v1/competitions"""
    pagination: PaginatedDict
    data: list[CompetitionItemDict]


class CompetitionDetailSeasonDict(TypedDict):
    season: str
    id: str


class V1CompetitionDetailResponse(RawResponseModel):
    """GET v1/competitions/{id}/details"""
    seasons: list[CompetitionDetailSeasonDict]
    code: str
    name: str
    id: str
```

### 6.2 `v1_team.py`

**Endpoint**: `v1/.../teams`

```python
# puller/interfaces/pulselive/v1_team.py
from typing import TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import (
    PaginatedDict,
    StadiumDict,
)


class TeamItemDict(TypedDict):
    id: str
    name: str
    shortName: str | None
    abbr: str
    stadium: StadiumDict


class V1TeamsResponse(RawResponseModel):
    """GET v1/competitions/{comp_id}/seasons/{season_id}/teams"""
    pagination: PaginatedDict
    data: list[TeamItemDict]
```

### 6.3 `v1_award.py`

**Endpoint**: `v1/.../awards`

```python
# puller/interfaces/pulselive/v1_award.py
from typing import TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import (
    CountryDict,
    PersonDict,
)


class AwardTeamDict(TypedDict):
    id: str
    name: str
    shortName: str
    loan: int | None


class AwardDatesDict(TypedDict):
    birth: str
    joinedClub: str


class AwardCareerDict(TypedDict):
    seasonsinPremierLeague: list[str]
    firstPremierLeagueFixtureId: str
    seasonsAtCurrentTeam: list[str]


class PlayerAwardDict(TypedDict):
    id: str
    currentTeam: AwardTeamDict
    date: str
    country: CountryDict
    name: PersonDict
    dates: AwardDatesDict
    type: str
    shirtNum: int
    weight: int
    countryOfBirth: str
    position: str
    preferredFoot: str
    height: int


class ManagerAwardDict(TypedDict):
    id: str
    currentTeam: AwardTeamDict
    date: str
    country: CountryDict
    name: PersonDict
    dates: AwardDatesDict
    type: str
    career: AwardCareerDict
    role: str


class V1AwardResponse(RawResponseModel):
    """GET v1/competitions/{comp_id}/seasons/{season_id}/awards"""
    managerAwards: list[ManagerAwardDict]
    playerAwards: list[PlayerAwardDict]
```

### 6.4 `v1_match.py`

**Endpoint**: `v1/.../matchweek/.../matches`, `v1/matches/{id}/events`, `v1/matches/{id}/officials`, `v1/matches/{id}/stats`

```python
# puller/interfaces/pulselive/v1_match.py
from typing import TypedDict

from pydantic import field_validator

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import (
    MatchTeamDict,
    PaginatedDict,
    PersonDict,
)
from football_data_manager.common.utils.pydantic_helper.string_to_float_validator import (
    convert_string_to_float,
)


# --- v1/matchweek matches ---

class MatchDict(TypedDict):
    kickoffTimezone: str
    period: str
    kickoff: str
    awayTeam: MatchTeamDict
    homeTeam: MatchTeamDict
    competition: str
    ground: str | None
    clock: str | None
    resultType: str | None
    matchId: str
    attendance: int | None


class V1MatchweekMatchesResponse(RawResponseModel):
    """GET v1/competitions/{comp_id}/seasons/{season_id}/matchweeks/{n}/matches"""
    pagination: PaginatedDict
    data: list[MatchDict]


# --- v1/matches/{id}/events ---

class EventBaseDict(TypedDict, total=False):
    """이벤트 기본 필드. total=False로 optional 처리."""
    period: str | None
    time: str | None
    timestamp: str | None


class EventCardDict(TypedDict, total=False):
    period: str | None
    time: str | None
    timestamp: str | None
    type: str
    playerId: str | None


class EventGoalDict(TypedDict, total=False):
    period: str | None
    time: str | None
    timestamp: str | None
    goalType: str
    assistPlayerId: str | None
    playerId: str


class EventSubDict(TypedDict, total=False):
    period: str | None
    time: str | None
    timestamp: str | None
    playerOnId: str | None
    playerOffId: str | None


class EventTeamDict(TypedDict):
    cards: list[EventCardDict]
    subs: list[EventSubDict]
    name: str
    id: str
    shortName: str
    goals: list[EventGoalDict]


class V1EventResponse(RawResponseModel):
    """GET v1/matches/{match_id}/events"""
    awayTeam: EventTeamDict
    homeTeam: EventTeamDict


# --- v1/matches/{id}/officials ---

class OfficialDict(TypedDict):
    official: PersonDict
    type: str


class V1MatchOfficialsResponse(RawResponseModel):
    """GET v1/matches/{match_id}/officials"""
    matchId: str
    matchOfficials: list[OfficialDict]


# --- v1/matches/{id}/stats ---

class MatchStatInfoModel(RawResponseModel):
    """경기 통계 상세. 문자열→float 변환이 필요하므로 BaseModel 유지.

    > 주의: 이 모델의 필드명은 API가 보내는 snake_case 원형 그대로입니다.
    > (Pulselive stats API는 camelCase가 아닌 snake_case를 사용)
    """
    accurate_back_zone_pass: float = 0.0
    accurate_chipped_pass: float = 0.0
    accurate_corners_intobox: float = 0.0
    accurate_cross: float = 0.0
    accurate_cross_nocorner: float = 0.0
    accurate_flick_on: float = 0.0
    accurate_freekick_cross: float = 0.0
    accurate_fwd_zone_pass: float = 0.0
    accurate_goal_kicks: float = 0.0
    accurate_keeper_sweeper: float = 0.0
    accurate_keeper_throws: float = 0.0
    accurate_launches: float = 0.0
    accurate_layoffs: float = 0.0
    accurate_long_balls: float = 0.0
    accurate_pass: float = 0.0
    accurate_pull_back: float = 0.0
    accurate_through_ball: float = 0.0
    accurate_throws: float = 0.0
    aerial_lost: float = 0.0
    aerial_won: float = 0.0
    # ... (전체 210+ 필드 동일하게 유지)

    @field_validator("*", mode="before")
    def convert_all_floats(cls, v):
        return convert_string_to_float(v)


class V1MatchTeamStatModel(RawResponseModel):
    """GET v1/matches/{match_id}/stats (list 내 개별 항목)"""
    side: str
    stats: MatchStatInfoModel
    teamId: str
```

> **참고**: `MatchStatInfoModel`과 `V1MatchTeamStatModel`은 `@field_validator` 때문에 BaseModel이며,
> 이름을 `...Response` 대신 `...Model`로 구분합니다. 또는 일관성을 위해 `...Response`를 유지해도 무방합니다.
> 실행 시 팀과 합의하세요.

### 6.5 `v1_player.py`

**Endpoint**: `v1/players/{id}`, `v1/.../players/{id}`

```python
# puller/interfaces/pulselive/v1_player.py
from datetime import datetime
from typing import TypedDict

from pydantic import RootModel, field_validator

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import (
    CountryDict,
    PersonDict,
)
from football_data_manager.common.utils.type_helper.datetime_helper import (
    parse_date_string_to_utc,
)


class PlayerTeamDict(TypedDict):
    name: str
    id: str
    shortName: str | None


class PlayerIdDict(TypedDict, total=False):
    competitionId: str | None
    seasonId: str | None
    playerId: str


class PlayerBaseModel(RawResponseModel):
    """Player 기본 모델. id 파싱 validator 필요하므로 BaseModel."""
    country: CountryDict
    currentTeam: PlayerTeamDict | None = None
    id: PlayerIdDict
    name: PersonDict
    position: str

    @field_validator("id", mode="before")
    def parse_id(cls, v) -> dict:
        if isinstance(v, str):
            return {"playerId": v}
        return v


class PlayerDatesModel(RawResponseModel):
    """Player dates. birth 파싱 validator 필요하므로 BaseModel."""
    birth: datetime | None = None
    joinedClub: str | None = None

    @field_validator("birth", mode="before")
    def parse_birth_date(cls, v) -> datetime | None:
        if isinstance(v, str):
            try:
                return parse_date_string_to_utc(v)
            except ValueError:
                return None
        return v


class PlayerDetailModel(PlayerBaseModel):
    """선수 상세 정보. PlayerBaseModel 상속."""
    loan: int | None = None
    countryOfBirth: str | None = None
    shirtNum: int | None = None
    weight: int | None = None
    dates: PlayerDatesModel
    preferredFoot: str | None = None
    height: int | None = None


# Type aliases
V1PlayerDetailsResponse = PlayerDetailModel
"""GET v1/competitions/{comp_id}/seasons/{season_id}/players/{player_id}"""

V1PlayerResponse = RootModel[list[PlayerDetailModel]]
"""GET v1/players/{player_id} (list 형태)"""
```

### 6.6 `v2_match.py`

**Endpoint**: `v2/matches/{id}`, `v3/matches/{id}/lineups`

```python
# puller/interfaces/pulselive/v2_match.py
from datetime import datetime
from typing import TypedDict

from pydantic import field_validator

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive._types import (
    MatchTeamDict,
    PersonDict,
)


# --- v2/matches/{id} ---

class SeasonInfoDict(TypedDict):
    name: str
    id: str


class V2MatchResponse(RawResponseModel):
    """GET v2/matches/{match_id}"""
    kickoffTimezone: str
    competitionId: str
    period: str
    matchWeek: int
    kickoff: datetime
    awayTeam: MatchTeamDict
    seasonInfo: SeasonInfoDict
    competition: str
    clock: str | None = None
    kickoffTimezoneString: str
    seasonId: str
    homeTeam: MatchTeamDict
    ground: str
    resultType: str | None = None
    matchId: str
    attendance: int | None = None

    @field_validator("kickoff", mode="before")
    def parse_custom_dt(cls, v) -> datetime:
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        return v


# --- v3/matches/{id}/lineups ---

class PlayerSimpleDict(TypedDict):
    firstName: str | None
    lastName: str | None
    display: str | None
    shirtNum: str
    isCaptain: bool
    id: str
    position: str
    subPosition: str | None


class ManagerDict(TypedDict, total=False):
    firstName: str | None
    lastName: str | None
    display: str | None
    id: str | None
    type: str | None


class FormationDict(TypedDict, total=False):
    subs: list[str] | None
    teamId: str | None
    lineup: list[list[str]] | None
    formation: str | None


class TeamLineupDict(TypedDict):
    players: list[PlayerSimpleDict]
    formation: FormationDict
    managers: list[ManagerDict]


class V3MatchLineupResponse(RawResponseModel):
    """GET v3/matches/{match_id}/lineups"""
    awayTeam: TeamLineupDict
    homeTeam: TeamLineupDict
```

### 6.7 `v2_player.py`

**Endpoint**: `v2/.../squad`, `v2/.../players/{id}/stats`

```python
# puller/interfaces/pulselive/v2_player.py
from typing import TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.pulselive.v1_player import (
    PlayerBaseModel,
    PlayerDetailModel,
)


# --- v2/.../squad ---

class V2SquadResponse(RawResponseModel):
    """GET v2/competitions/{comp_id}/seasons/{season_id}/teams/{team_id}/squad"""
    players: list[PlayerDetailModel]


# --- v2/.../players/{id}/stats ---

class PlayerStatsDict(TypedDict, total=False):
    """선수 통계. 모든 필드 optional."""
    appearances: float | None
    blockedShots: float | None
    aerialDuels: float | None
    aerialDuelsWon: float | None
    groundDuels: float | None
    groundDuelsWon: float | None
    duels: float | None
    duelsWon: float | None
    totalFoulsConceded: float | None
    interceptions: float | None
    possessionWonFinalThird: float | None
    recoveries: float | None
    totalTackles: float | None
    tacklesWon: float | None
    totalRedCards: float | None
    straightRedCards: float | None
    yellowCards: float | None
    cleanSheets: float | None
    goalsConceded: float | None
    expectedGoalsOnTargetConceded: float | None
    catches: float | None
    penaltiesFaced: float | None
    penaltyGoalsConceded: float | None
    savesMade: float | None
    successfulLongPasses: float | None
    unsuccessfulLongPasses: float | None
    goalAssists: float | None
    keyPassesAttemptAssists: float | None
    expectedAssists: float | None
    successfulShortPasses: float | None
    totalPasses: float | None
    successfulCrossesAndCorners: float | None
    unsuccessfulCrossesAndCorners: float | None
    successfulDribbles: float | None
    unsuccessfulDribbles: float | None
    totalFoulsWon: float | None
    touches: float | None
    totalTouchesInOppositionBox: float | None
    expectedGoals: float | None
    penaltiesTaken: float | None
    expectedGoalsOnTarget: float | None
    goals: float | None
    penaltyGoals: float | None
    totalShots: float | None
    shotsOnTargetIncGoals: float | None


class V2PlayerStatResponse(RawResponseModel):
    """GET v2/competitions/{comp_id}/seasons/{season_id}/players/{player_id}/stats"""
    player: PlayerBaseModel
    stats: PlayerStatsDict
```

### 6.8 `v2_team_stat.py`

**Endpoint**: `v2/.../teams/{id}/stats`

```python
# puller/interfaces/pulselive/v2_team_stat.py
from typing import TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel


class TeamSimpleDict(TypedDict):
    id: str
    name: str
    shortName: str
    abbr: str


class TeamStatsDict(TypedDict, total=False):
    """팀 통계. 모든 필드 optional. 120+ 필드."""
    duelsLost: float | None
    penaltiesSaved: float | None
    blockedShots: float | None
    shotsOnTargetInclGoals: float | None
    expectedGoalsOnTarget: float | None
    gamesPlayed: float | None
    crossingAccuracy: float | None
    totalPasses: float | None
    goals: float | None
    offsides: float | None
    awayGoals: float | None
    tackleSuccess: float | None
    # ... (전체 120+ 필드 camelCase로 작성)


class V2TeamStatsResponse(RawResponseModel):
    """GET v2/competitions/{comp_id}/seasons/{season_id}/teams/{team_id}/stats"""
    stats: TeamStatsDict
    team: TeamSimpleDict
```

---

## 7. Step 4: The Athletic 파일 재구성

- [ ] **완료**

### 7.1 `league_feed.py`

The Athletic GraphQL은 snake_case를 사용합니다. 원형 보존 = snake_case 유지.

```python
# puller/interfaces/the_athletic/league_feed.py
from typing import TypedDict

from pydantic import BaseModel

from football_data_manager.puller.interfaces.base import RawResponseModel
from football_data_manager.puller.interfaces.the_athletic._types import AuthorDict


class LeagueFeedContentDict(TypedDict, total=False):
    __typename: str
    title: str | None
    consumable_id: str | None
    author: AuthorDict | None
    excerpt: str | None
    image_uri: str | None
    permalink: str | None


class LeagueFeedLayoutDict(TypedDict):
    __typename: str
    type: str
    typename: str
    contents: list[LeagueFeedContentDict]


class LeagueFeedMulliganDict(TypedDict):
    __typename: str
    layouts: list[LeagueFeedLayoutDict]


class LeagueFeedResponse(RawResponseModel):
    """LeagueFeedQuery GraphQL 응답"""
    feedMulligan: LeagueFeedMulliganDict


class QueryVariables(BaseModel):
    """GraphQL query variables (요청용, 응답 아님)."""
    feed: str = "league"
    feed_id: int
    is_mobile_web: bool = False
    locale: str = "en-gb"
    show_long_titles: bool = False
    page: int = 0
    retrieveMeta: bool = False
```

### 7.2 `news.py`

```python
# puller/interfaces/the_athletic/news.py
from typing import TypedDict

from football_data_manager.puller.interfaces.base import RawResponseModel


class ArticleAuthorDict(TypedDict):
    name: str
    url: str
    sameAs: str | list[str] | None


class ArticleResponse(RawResponseModel):
    """Article 응답"""
    author: list[ArticleAuthorDict]
    dateCreated: str
    datePublished: str
    dateModified: str
    articleBody: str | None = None
    description: str
    headline: str
    thumbnailUrl: str


class NewsTranslateObjectDict(TypedDict):
    en: str
    ko: str


class NewsTranslateSummaryDict(TypedDict):
    en: list[str]
    ko: list[str]


class NewsTranslateResponse(RawResponseModel):
    """뉴스 번역 응답"""
    article: int
    authors: list[NewsTranslateObjectDict]
    title: NewsTranslateObjectDict
    summary: NewsTranslateSummaryDict
    teams: list[str]
```

---

## 8. Step 5: Client import 경로 수정

- [ ] **완료**

### 8.1 영향 범위

| 파일 | 변경 내용 |
|------|----------|
| `clients/pulselive.py` | 모든 Response import 경로 변경 |
| `clients/the_athletic.py` | LeagueFeedResponse, QueryVariables import 경로 변경 |
| `pullers/pulselive/*.py` | Response model import 경로 변경 |
| `pullers/the_athletic/news.py` | LeagueFeedResponse import 경로 변경 |
| `container.py` | 변경 없음 (Puller만 import) |

### 8.2 주요 import 변경 예시

```python
# Before (clients/pulselive.py)
from football_data_manager.puller.interfaces.pulselive.competition import (
    V1CompetitionResponse, V1CompetitionDetailResponse,
)
from football_data_manager.puller.interfaces.pulselive.player import (
    V1PlayerResponse, V1PlayerDetailsResponse,
)

# After
from football_data_manager.puller.interfaces.pulselive.v1_competition import (
    V1CompetitionResponse, V1CompetitionDetailResponse,
)
from football_data_manager.puller.interfaces.pulselive.v1_player import (
    V1PlayerResponse, V1PlayerDetailsResponse,
)
```

---

## 9. Step 6: 검증

- [ ] **완료**

### 9.1 Import 검증

```python
python -c "
from football_data_manager.puller.interfaces.base import CamelCaseModel, RawResponseModel
from football_data_manager.puller.interfaces.pulselive.v1_competition import V1CompetitionResponse
from football_data_manager.puller.interfaces.pulselive.v1_team import V1TeamsResponse
from football_data_manager.puller.interfaces.pulselive.v1_award import V1AwardResponse
from football_data_manager.puller.interfaces.pulselive.v1_match import V1MatchweekMatchesResponse
from football_data_manager.puller.interfaces.pulselive.v1_player import V1PlayerDetailsResponse
from football_data_manager.puller.interfaces.pulselive.v2_match import V2MatchResponse, V3MatchLineupResponse
from football_data_manager.puller.interfaces.pulselive.v2_player import V2SquadResponse, V2PlayerStatResponse
from football_data_manager.puller.interfaces.pulselive.v2_team_stat import V2TeamStatsResponse
from football_data_manager.puller.interfaces.the_athletic.league_feed import LeagueFeedResponse
print('All imports OK')
"
```

### 9.2 원형 보존 검증

```python
python -c "
from football_data_manager.puller.interfaces.pulselive.v1_competition import V1CompetitionDetailResponse

# API 응답 원형 (camelCase) 그대로 파싱 확인
data = {
    'seasons': [{'season': '2024/2025', 'id': '578'}],
    'code': 'EN_PR',
    'name': 'Premier League',
    'id': '1'
}
r = V1CompetitionDetailResponse.model_validate(data)
assert r.code == 'EN_PR'
assert r.seasons[0]['season'] == '2024/2025'
print('Raw preservation: OK')
"
```

### 9.3 TypedDict 검증

```python
python -c "
from football_data_manager.puller.interfaces.pulselive._types import PersonDict
from typing import get_type_hints
import typing

# TypedDict인지 확인
assert typing.is_typeddict(PersonDict)
print('TypedDict verification: OK')
"
```

---

## 10. BaseModel vs TypedDict 판정 기준

### 10.1 판정 플로우차트

```
이 모델에 @field_validator가 있는가?
  ├─ Yes → BaseModel (RawResponseModel)
  └─ No
      └─ model_validate()의 직접 대상인가? (Client 메서드에서 반환)
          ├─ Yes → BaseModel (RawResponseModel)
          └─ No → TypedDict
```

### 10.2 전체 판정 결과

| 모델 | 타입 | 이유 |
|------|------|------|
| **Top-level Response (15개)** | BaseModel | `model_validate()` 대상 |
| `MatchStatInfoModel` | BaseModel | `@field_validator("*")` string→float |
| `V1MatchTeamStatModel` | BaseModel | MatchStatInfoModel 참조 + top-level |
| `PlayerBaseModel` | BaseModel | `@field_validator("id")` |
| `PlayerDatesModel` | BaseModel | `@field_validator("birth")` |
| `PlayerDetailModel` | BaseModel | PlayerBaseModel 상속 |
| `V2MatchResponse` | BaseModel | `@field_validator("kickoff")` |
| **그 외 모든 중첩 모델** | TypedDict | 검증 불필요 |

### 10.3 TypedDict 전환 대상 (현재 BaseModel → TypedDict)

| 현재 클래스 | 새 TypedDict | 파일 |
|------------|-------------|------|
| `PersonResponse` | `PersonDict` | `_types.py` |
| `CountryResponse` | `CountryDict` | `_types.py` |
| `StadiumResponse` | `StadiumDict` | `_types.py` |
| `ManagerResponse` | `ManagerDict` | `v2_match.py` |
| `PaginatedResponse` | `PaginatedDict` | `_types.py` |
| `CompetitionItemResponse` | `CompetitionItemDict` | `v1_competition.py` |
| `CompetitionDetailSeasonResponse` | `CompetitionDetailSeasonDict` | `v1_competition.py` |
| `SeasonResponse` | `SeasonInfoDict` | `v2_match.py` |
| `TeamResponse` | `TeamItemDict` | `v1_team.py` |
| `TeamSimpleResponse` | `TeamSimpleDict` | `v2_team_stat.py` |
| `MatchTeamResponse` | `MatchTeamDict` | `_types.py` |
| `MatchResponse` | `MatchDict` | `v1_match.py` |
| `AwardBaseResponse` | (통합) | `v1_award.py` |
| `AwardCareerResponse` | `AwardCareerDict` | `v1_award.py` |
| `AwardDatesResponse` | `AwardDatesDict` | `v1_award.py` |
| `AwardTeamResponse` | `AwardTeamDict` | `v1_award.py` |
| `PlayerAwardResponse` | `PlayerAwardDict` | `v1_award.py` |
| `ManagerAwardResponse` | `ManagerAwardDict` | `v1_award.py` |
| `EventCardResponse` | `EventCardDict` | `v1_match.py` |
| `EventGoalResponse` | `EventGoalDict` | `v1_match.py` |
| `EventSubResponse` | `EventSubDict` | `v1_match.py` |
| `EventTeamResponse` | `EventTeamDict` | `v1_match.py` |
| `OfficialResponse` | `OfficialDict` | `v1_match.py` |
| `FormationResponse` | `FormationDict` | `v2_match.py` |
| `TeamLineupResponse` | `TeamLineupDict` | `v2_match.py` |
| `PlayerSimpleResponse` | `PlayerSimpleDict` | `v2_match.py` |
| `PlayerStatsResponse` | `PlayerStatsDict` | `v2_player.py` |
| `TeamStatsResponse` | `TeamStatsDict` | `v2_team_stat.py` |
| (The Athletic 7개) | (각 `...Dict`) | `league_feed.py`, `news.py` |

---

## 11. 검증 체크리스트

### 11.1 구조 검증

- [ ] 기존 도메인별 파일 삭제 (common.py, player.py, team.py 등)
- [ ] Endpoint별 새 파일 생성 완료
- [ ] `_types.py` 공유 TypedDict 정의 완료
- [ ] `base.py`에 `CamelCaseModel` 유지 + `RawResponseModel` 추가 완료

### 11.2 원형 보존 검증

- [ ] Pulselive 모델 필드명이 API camelCase와 일치
- [ ] The Athletic 모델 필드명이 API snake_case와 일치
- [ ] `puller/interfaces/` 내 모든 모델이 `RawResponseModel` 사용 (`CamelCaseModel` 미사용)

### 11.3 TypedDict 검증

- [ ] `@field_validator` 있는 모델만 BaseModel
- [ ] 나머지 모든 중첩 모델이 TypedDict
- [ ] `typing.is_typeddict()` 검증 통과

### 11.4 Client/Puller 연동 검증

- [ ] `PulseliveClient` 15개 메서드 정상 import
- [ ] `TheAthleticClient` 메서드 정상 import
- [ ] 모든 Puller import 경로 수정 완료
- [ ] `PullerContainer` 초기화 정상

---

## 12. 완료 기준

### 12.1 필수 기준

- [ ] `puller/interfaces/` 내 모든 모델이 `RawResponseModel` 또는 TypedDict 사용
- [ ] `CamelCaseModel`은 `base.py`에 유지 (다른 모듈 활용 가능)
- [ ] 모든 필드명이 API 원형 키와 동일
- [ ] TypedDict 적용률 70% 이상 (BaseModel은 validator 필요한 곳만)
- [ ] Endpoint별 파일 구성 완료
- [ ] 모든 Client/Puller import 정상

### 12.2 품질 기준

- [ ] 파일명만으로 Endpoint 식별 가능
- [ ] `_types.py`에 공유 TypedDict 집중
- [ ] `CamelCaseModel`과 `RawResponseModel`의 역할 분리 명확
- [ ] Phase 2의 모든 기능 동일 유지

---

## 사전 확인 필요 사항

> **중요**: 실행 전 Pulselive API의 실제 JSON 응답을 확인하여 필드명(camelCase vs snake_case)을
> 검증해야 합니다. 특히 stats 관련 endpoint (`v1/.../stats`, `v2/.../stats`)의 필드명이
> camelCase인지 snake_case인지에 따라 모델 필드명이 달라집니다.
>
> ```bash
> # 실제 API 응답 확인 예시 (curl)
> curl -s "https://sdp-prem-prod.premier-league-prod.pulselive.com/api/v1/competitions" | python -m json.tool | head -20
> ```
>
> 확인 결과에 따라 stat 모델 필드명을 camelCase 또는 snake_case로 확정합니다.

---

*문서 생성일: 2026-02-02*
*마지막 수정: 2026-02-02*
