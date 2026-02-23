# Phase 3: Merger 구현

**상태**: 진행 중 🚧 (핵심 구현 완료, 통합 테스트만 남음)
**목표**: Merger 컴포넌트 전면 구현 (데이터 병합 + 번역 + 리소스 검증 + Association 관리)
**선행 조건**: Phase 2 완료 ✅

> **시작 전에**: 이 문서는 실행 가이드입니다. 전체 계획은 `1_master_plan.md` Section 4.3을 참고하세요.

---

## 목차

1. [개요](#1-개요)
2. [Step 1: 디렉토리 구조 생성](#2-step-1-디렉토리-구조-생성)
3. [Step 2: 공통 서비스 구현](#3-step-2-공통-서비스-구현)
4. [Step 3: CompetitionMerger 구현](#4-step-3-competitionmerger-구현)
5. [Step 4: SeasonMerger 구현](#5-step-4-seasonmerger-구현)
6. [Step 5: GroundMerger + TeamMerger 구현](#6-step-5-groundmerger--teammerger-구현)
7. [Step 6: PlayerMerger 구현](#7-step-6-playermerger-구현)
8. [Step 7: FixtureMerger 구현](#8-step-7-fixturemerger-구현)
9. [Step 8: MatchMerger 구현](#9-step-8-matchmerger-구현)
10. [Step 9: MatchStatMerger 구현](#10-step-9-matchstatmerger-구현)
11. [Step 10: PlayerStatMerger 구현](#11-step-10-playerstatmerger-구현)
12. [Step 11: TeamStatMerger 구현](#12-step-11-teamstatmerger-구현)
13. [Step 12: AwardMerger 구현](#13-step-12-awardmerger-구현)
14. [Step 13: NewsMerger 구현](#14-step-13-newsmerger-구현)
15. [Step 14: PlayerStatScorer 구현](#15-step-14-playerstatscorer-구현)
16. [Step 15: MergerContainer 구현](#16-step-15-mergercontainer-구현)
17. [Step 16: 검증](#17-step-16-검증)
18. [검증 체크리스트](#18-검증-체크리스트)
19. [Phase 3 완료 기준](#19-phase-3-완료-기준)
20. [다음 단계](#20-다음-단계)

---

## 1. 개요

### 1.1 Phase 3 범위

Phase 3는 Merger 컴포넌트를 구현하는 단계입니다. Merger는 Puller가 수집한 API 응답 데이터를 DB Entity로 변환/병합합니다:

- **공통 서비스 복원**: `TranslatorService` (Anthropic Claude), `ResourceValidationClient` (URL 검증)
- **11개 Merger 구현**: Competition, Season, Team(+Ground), Player, Fixture, Match, MatchStat, PlayerStat, TeamStat, Award, News
- **PlayerStatScorer**: 선수 점수 계산 (6개 카테고리)
- **DI Container**: `MergerContainer` 구현

### 1.2 설계 원칙 (from `1_master_plan.md`)

- **추상 클래스 사용 안 함**: 각 Merger가 고유한 로직을 가짐
- **구체적 Merger만 구현**: 필요한 메서드만 정의
- **멀티 소스 지원**: 하나의 Merger가 여러 Response 타입 처리 가능

### 1.3 공통 패턴: Check → Translate → Validate → Create/Update

모든 Merger는 다음 4단계 패턴을 따릅니다:

```
1. Check:    repository.get_by_pulselive_id(source_id) → 존재 여부 확인
2. Translate: translator.translate_word(name_en) → name_kr (필요 시)
3. Validate:  resource_client.validate_url_exists(url) → 리소스 URL 검증 (필요 시)
4. Upsert:   repository.create(entity) 또는 repository.update(entity)
```

### 1.4 현재 상태 (Phase 2 완료 후)

```
football_data_manager/
├── repository/                   # ✅ Phase 1 완료
│   ├── entities/                 # 15 Entity + 11 Association
│   ├── repositories/             # 15 Repository + base + pulselive
│   ├── session.py
│   └── container.py
├── puller/                       # ✅ Phase 2 완료
│   ├── interfaces/               # 14 interface 파일
│   ├── clients/                  # 2 client (pulselive, the_athletic)
│   ├── pullers/                  # 11 puller (10 pulselive + 1 the_athletic)
│   └── container.py
├── common/
│   ├── enums/                    # ✅ 유지
│   ├── services/config/          # ✅ 유지
│   └── utils/                    # ✅ 유지
└── merger/                       # ❌ 아직 없음
```

### 1.5 Phase 3 완료 후 목표 구조

```
football_data_manager/
├── repository/                   # Phase 1 ✅
├── puller/                       # Phase 2 ✅
├── merger/                       # ★ 새로 생성
│   ├── __init__.py
│   ├── services/                 # 공통 서비스
│   │   ├── __init__.py
│   │   ├── translator.py         # TranslatorService (Anthropic Claude)
│   │   └── resource_validator.py # ResourceValidationClient (URL HEAD 검증)
│   ├── mergers/                  # 개별 Merger
│   │   ├── __init__.py
│   │   ├── competition.py        # CompetitionMerger
│   │   ├── season.py             # SeasonMerger
│   │   ├── team.py               # TeamMerger + GroundMerger
│   │   ├── player.py             # PlayerMerger
│   │   ├── fixture.py            # FixtureMerger
│   │   ├── match.py              # MatchMerger
│   │   ├── match_stat.py         # MatchStatMerger
│   │   ├── player_stat.py        # PlayerStatMerger
│   │   ├── team_stat.py          # TeamStatMerger
│   │   ├── award.py              # AwardMerger
│   │   └── news.py               # NewsMerger
│   ├── scorer.py                 # PlayerStatScorer (점수 계산)
│   └── container.py              # MergerContainer (DI)
└── common/                       # 유지
```

### 1.6 파일 수 요약

| 디렉토리 | 파일 수 | 설명 |
|----------|---------|------|
| `merger/services/` | 3 | __init__.py + translator + resource_validator |
| `merger/mergers/` | 12 | __init__.py + 11 merger 파일 |
| `merger/` | 3 | __init__.py + scorer + container |
| **총** | **18** | |

### 1.7 Merger별 복잡도 및 구현 순서

| 순서 | Merger | 복잡도 | 번역 | URL검증 | Association | 비고 |
|------|--------|--------|------|---------|-------------|------|
| 1 | CompetitionMerger | 낮음 | ✅ | ❌ | ❌ | 하드코딩 ID 필터 |
| 2 | SeasonMerger | 중간 | ❌ | ❌ | ❌ | 날짜 파생 (matchweek 이진검색) |
| 3 | GroundMerger | 낮음 | ✅ | ❌ | ❌ | TeamMerger 내부 |
| 3 | TeamMerger | 중간 | ✅ | ✅ | ❌ | Ground 먼저 생성 후 Team 생성 |
| 4 | PlayerMerger | 중간 | ✅ | ✅ | ❌ | 국적 번역 캐싱 패턴 |
| 5 | FixtureMerger | 중간 | ❌ | ❌ | ❌ | Team/Ground FK 조회 필요 |
| 6 | MatchMerger | **높음** | ✅ | ❌ | ✅×5 | 4개 API, Staff/Official 생성 |
| 7 | MatchStatMerger | 중간 | ❌ | ❌ | ❌ | 경기당 2개 (Home/Away) |
| 8 | PlayerStatMerger | 중간 | ❌ | ❌ | ❌ | 파생 필드 다수 |
| 9 | TeamStatMerger | **높음** | ❌ | ❌ | ✅ | 2-phase (DB파생 + API) |
| 10 | AwardMerger | 중간 | ✅ | ❌ | ✅×2 | PlayerStat/Staff association |
| 11 | NewsMerger | **높음** | ✅ | ❌ | ✅ | 웹스크래핑, LLM 번역 |

### 1.8 Archive 참조 경로

| 파일 | Archive 경로 |
|------|-------------|
| TranslatorService | `archive/football_data_manager/common/services/translator/translatorService.py` |
| ResourceValidationClient | `archive/football_data_manager/common/services/client/resource_validation_client.py` |
| CompetitionPuller | `archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_competition_puller.py` |
| SeasonPuller | `archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_season_puller.py` |
| TeamPuller | `archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_team_puller.py` |
| PlayerPuller | `archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_player_puller.py` |
| FixturePuller | `archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_fixture_puller.py` |
| MatchPuller | `archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_match_puller.py` |
| MatchStatPuller | `archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_match_stat_puller.py` |
| PlayerStatsPuller | `archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_player_stats_puller.py` |
| TeamStatsPuller | `archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_team_stats_puller.py` |
| AwardPuller | `archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_award_puller.py` |
| TheAthleticPuller | `archive/football_data_manager/puller/services/the_athletic/the_athletic_puller_service.py` |
| PlayerStatScorer | `archive/legacy_scripts/backfill_player_stat_scores.py` |

---

## 2. Step 1: 디렉토리 구조 생성

### 2.1 체크리스트

- [x] `merger/` 디렉토리 생성
- [x] `merger/__init__.py` 생성 (빈 파일)
- [x] `merger/services/` 디렉토리 생성
- [x] `merger/services/__init__.py` 생성 (빈 파일)
- [x] `merger/mergers/` 디렉토리 생성
- [x] `merger/mergers/__init__.py` 생성 (빈 파일)

### 2.2 생성 명령어

```bash
mkdir -p football_data_manager/merger/{services,mergers}
touch football_data_manager/merger/__init__.py
touch football_data_manager/merger/services/__init__.py
touch football_data_manager/merger/mergers/__init__.py
```

### 2.3 검증

```bash
# 디렉토리 구조 확인
find football_data_manager/merger -type f | sort
# 예상 출력:
# football_data_manager/merger/__init__.py
# football_data_manager/merger/mergers/__init__.py
# football_data_manager/merger/services/__init__.py
```

---

## 3. Step 2: 공통 서비스 구현

### 3.1 체크리스트

- [x] `merger/services/translator.py` 구현 (TranslatorService)
- [x] `merger/services/resource_validator.py` 구현 (ResourceValidationClient)
- [x] Import 검증

### 3.2 TranslatorService

**파일**: `merger/services/translator.py`
**Archive 참조**: `archive/.../common/services/translator/translatorService.py`

**핵심 인터페이스**:

```python
class TranslatorService:
    """Anthropic Claude API를 사용한 영한 번역 서비스"""

    def __init__(self, config_service: ConfigService):
        self._client = anthropic.AsyncAnthropic(api_key=config_service.anthropic_api_key)

    async def translate_word(self, word: str) -> str:
        """단일 단어/구문 영한 번역. 5회 재시도."""
        ...

    async def close(self) -> None:
        """리소스 정리"""
        ...
```

**구현 사항**:

- [x] Anthropic AsyncAnthropic 클라이언트 초기화
- [x] 시스템 프롬프트 구성 (축구 도메인 전문 번역 예시 포함)
- [x] JSON 응답 파싱: `{"original": "...", "translated": "..."}`
- [x] 5회 재시도 + 1초 sleep 로직
- [x] 에러 핸들링 (API 실패 시 원문 반환)

**번역 프롬프트 예시** (archive에서 보존):

```
- "Premier League" -> "프리미어 리그"
- "Manchester United" -> "맨체스터 유나이티드"
- "Erling Haaland" -> "엘링 홀란드"
```

### 3.3 ResourceValidationClient

**파일**: `merger/services/resource_validator.py`
**Archive 참조**: `archive/.../common/services/client/resource_validation_client.py`

**핵심 인터페이스**:

```python
class ResourceValidationClient:
    """HTTP HEAD 요청으로 리소스 URL 존재 여부 검증 (캐싱 포함)"""

    def __init__(self):
        self._client = httpx.AsyncClient()
        self._cache: dict[str, bool] = {}

    async def validate_url_exists(self, url: str) -> bool:
        """URL이 유효한지 HEAD 요청으로 확인. 캐시 활용."""
        ...

    def clear_cache(self) -> None:
        """캐시 초기화"""
        ...

    async def close(self) -> None:
        """httpx 클라이언트 종료"""
        ...
```

**구현 사항**:

- [x] httpx.AsyncClient 초기화
- [x] HTTP HEAD 요청 (GET 아님 — 대역폭 절약)
- [x] 결과 캐싱 (`Dict[str, bool]`)
- [x] HTTP 200만 `True` 반환
- [x] 타임아웃 및 네트워크 에러 핸들링 (`False` 반환)

### 3.4 ConfigService 확장 확인

TranslatorService는 `config_service.api_list.anthropic.key`를 사용합니다:

- [x] `ConfigService`에서 `api_list.anthropic.key` 접근 가능 여부 확인
- [x] 없으면 `.env` 및 `ConfigService`에 추가 (현재는 `api_list.anthropic.key` 사용으로 추가 불필요)

---

## 4. Step 3: CompetitionMerger 구현

### 4.1 체크리스트

- [x] `merger/mergers/competition.py` 구현
- [x] 하드코딩 ID 필터 구현: `["1", "2", "5", "6", "8", "1007", "1125"]`
- [x] 번역 통합 (name_en → name_kr)
- [x] Import 및 단위 테스트

### 4.2 API → Entity 필드 매핑

**소스 Puller**: `CompetitionPuller.pull_competitions()` → `V1CompetitionResponse`

| API 필드 (`CompetitionItemDict`) | Entity 필드 (`CompetitionEntity`) |
|---|---|
| `item["code"]` | `abbreviation` |
| `item["name"]` | `name_en` |
| `translate_word(item["name"])` | `name_kr` |
| `str(item["id"])` | `source_id` |

### 4.3 Flow

```python
class CompetitionMerger:
    ALLOWED_IDS = ["1", "2", "5", "6", "8", "1007", "1125"]

    def __init__(self, competition_repo, translator):
        ...

    async def merge(self, response: V1CompetitionResponse) -> list[CompetitionEntity]:
        results = []
        for item in response.data:
            if item["id"] not in self.ALLOWED_IDS:
                continue
            existing = await self._repo.get_by_pulselive_id(item["id"])
            if existing:
                results.append(existing)
                continue
            name_kr = await self._translator.translate_word(item["name"])
            entity = CompetitionEntity(
                abbreviation=item["code"],
                name_en=item["name"],
                name_kr=name_kr,
                source_id=item["id"],
            )
            created = await self._repo.create(entity)
            results.append(created)
        return results
```

---

## 5. Step 4: SeasonMerger 구현

### 5.1 체크리스트

- [x] `merger/mergers/season.py` 구현
- [x] 시즌명에서 연도 파싱 (`"Season 2024/2025"` → `2024, 2025`)
- [x] 약칭 생성 (`"24/25"`)
- [x] Matchweek 이진검색으로 `date_start`, `date_end` 파생
- [x] Import 및 단위 테스트

### 5.2 API → Entity 필드 매핑

**소스 Puller**:
- `SeasonPuller.pull_seasons()` → `V1CompetitionDetailResponse` (시즌 목록)
- `FixturePuller.pull_matchweek_matches()` → `V1MatchweekMatchesResponse` (날짜 파생용)

| 파생 방식 | Entity 필드 (`SeasonEntity`) |
|---|---|
| 시즌명에서 파싱 (e.g. `"24/25"`) | `abbreviation` |
| `competition` entity (FK) | `competition_id` |
| Matchweek 이진검색 (마지막 matchweek) | `date_end` |
| Matchweek 1 최초 kickoff | `date_start` |
| `item["id"]` | season_source_id (source_id 조합에 사용) |
| 시즌명에서 파싱 | `year_end`, `year_start` |

### 5.3 source_id 생성 패턴

```python
source_id = f"{competition.source_id}_{season_api_id}"
```

### 5.4 날짜 파생 로직 (archive 참조)

```python
# date_start: matchweek 1의 가장 이른 kickoff
matchweek_1 = await fixture_puller.pull_matchweek_matches(comp_id, season_id, 1)
date_start = min(parse_kickoff(m) for m in matchweek_1.data)

# date_end: 이진검색으로 마지막 matchweek 탐색
# 시작: matchweek 50 → 데이터 없으면 범위 축소
# 마지막 matchweek의 가장 늦은 kickoff
```

---

## 6. Step 5: GroundMerger + TeamMerger 구현

### 6.1 체크리스트

- [x] `merger/mergers/team.py` 구현 (GroundMerger + TeamMerger 동일 파일)
- [x] GroundMerger: Ground 존재 여부 확인 후 생성 (번역 포함)
- [x] TeamMerger: Team badge URL 검증, 번역 포함
- [x] Ground → Team 순서 보장 (Ground FK 필요)
- [x] Import 및 단위 테스트

### 6.2 Ground: API → Entity 필드 매핑

**소스**: `V1TeamsResponse.data[].stadium` (StadiumDict)

| API 필드 (`StadiumDict`) | Entity 필드 (`GroundEntity`) |
|---|---|
| `stadium["city"]` | `city_name_en` |
| `translate_word(stadium["city"])` | `city_name_kr` |
| `stadium["name"]` | `name_en` |
| `translate_word(stadium["name"])` | `name_kr` |
| `stadium["capacity"]` | `capacity` |

**source_id**: `GroundEntity.get_source_id(name_en)` — MD5 해시 기반

### 6.3 Team: API → Entity 필드 매핑

**소스 Puller**: `TeamPuller.pull_teams()` → `V1TeamsResponse`

| API 필드 (`TeamItemDict`) | Entity 필드 (`TeamEntity`) |
|---|---|
| `item["abbr"]` | `abbreviation` |
| `item["name"]` | `name_en` |
| `translate_word(item["name"])` | `name_kr` |
| `item["shortName"] or item["name"]` | `short_name_en` |
| `translate_word(short_name)` | `short_name_kr` |
| `str(item["id"])` | `source_id` |
| 검증된 badge URL | `icon_url` |

### 6.4 리소스 URL 패턴

```python
# Team badge
f"https://resources.premierleague.com/premierleague25/badges-alt/{team_source_id}.svg"
```

### 6.5 기존 Team 업데이트 조건

- `icon_url`이 비어있으면 → badge URL 검증 후 업데이트

---

## 7. Step 6: PlayerMerger 구현

### 7.1 체크리스트

- [x] `merger/mergers/player.py` 구현
- [x] 번역 캐싱 패턴 구현 (국적 번역: 메모리 캐시 → DB 조회 → API 번역)
- [x] Photo URL, Flag URL 검증
- [x] PositionEnum, SideEnum 매핑
- [x] Import 및 단위 테스트

### 7.2 API → Entity 필드 매핑

**소스 Puller**: `PlayerPuller.pull_squad()` → `V2SquadResponse`

| API 필드 (`PlayerDetailResponse`) | Entity 필드 (`PlayerEntity`) |
|---|---|
| `player.country_of_birth` | `birth_country` |
| `player.dates.birth` | `birth_date` |
| `player.name.simple_name` | `display_name_en` |
| `translate_word(name.simple_name)` | `display_name_kr` |
| `player.name.full_name` | `full_name` |
| `player.country.country` | `nationality_en` |
| 캐싱된 번역 결과 | `nationality_kr` |
| 검증된 flag URL | `nationality_flag_icon_url` |
| `PositionEnum.from_string(player.position)` | `position` |
| `SideEnum.from_string(player.preferred_foot)` | `preferred_foot` |
| `player.id.player_id` | `source_id` |
| `player.height` | `height` |
| `player.weight` | `weight` |
| 검증된 photo URL | `photo_url` |

### 7.3 리소스 URL 패턴

```python
# Player photo
f"https://resources.premierleague.com/premierleague25/photos/players/110x140/{player_source_id}.png"

# Nationality flag
f"https://resources.premierleague.com/premierleague/flags/{iso_code}.png"
```

### 7.4 국적 번역 캐싱 패턴 (3단계)

```python
# 1. 메모리 캐시 확인
if country_en in self._country_cache:
    return self._country_cache[country_en]

# 2. DB 조회 (이미 번역된 다른 선수의 국적)
db_result = await self._player_repo.get_nationality_kr(country_en)
if db_result:
    self._country_cache[country_en] = db_result
    return db_result

# 3. API 번역
translated = await self._translator.translate_word(country_en)
self._country_cache[country_en] = translated
return translated
```

### 7.5 기존 Player 업데이트 조건

- `photo_url`이 비어있으면 → photo URL 검증 후 업데이트

---

## 8. Step 7: FixtureMerger 구현

### 8.1 체크리스트

- [x] `merger/mergers/fixture.py` 구현
- [x] Home/Away Team FK 조회 (source_id로)
- [x] Ground FK 조회 (name으로, 쉼표 앞 부분 사용)
- [x] kickoff_time UTC 변환
- [x] 배치 생성 (`create_many`)
- [x] Import 및 단위 테스트

### 8.2 API → Entity 필드 매핑

**소스 Puller**: `FixturePuller.pull_matchweek_matches()` → `V1MatchweekMatchesResponse`

| API 필드 (`MatchDict`) | Entity 필드 (`FixtureEntity`) |
|---|---|
| `match["awayTeam"]["id"]` → DB 조회 | `away_team_id` (FK) |
| `matchweek_number` (파라미터) | `game_week` |
| `match["homeTeam"]["id"]` → DB 조회 | `home_team_id` (FK) |
| `create_utc(match["kickoff"], match["kickoffTimezone"])` | `kickoff_time` |
| `season` entity (FK) | `season_id` |
| `match["matchId"]` | `source_id` |
| `match["ground"].split(",")[0]` → DB 조회 | `ground_id` (FK, nullable) |

---

## 9. Step 8: MatchMerger 구현

### 9.1 체크리스트

- [x] `merger/mergers/match.py` 구현
- [x] 4개 API 응답 처리 (v2/match, v1/events, v3/lineups, v1/officials)
- [x] StaffEntity 생성 (managers, 번역 포함)
- [x] OfficialEntity 생성 (번역 포함)
- [x] MatchEntity 생성
- [x] 5개 Association 테이블 채우기 (lineup, substitute, card, goal, substitution)
- [x] FULLTIME 경기 스킵 로직
- [x] 누락 Player fallback 생성 (v1/player API)
- [x] Import 및 단위 테스트

### 9.2 소스 Pullers

| Puller 메서드 | 반환 타입 | 용도 |
|---|---|---|
| `MatchPuller.pull_match()` | `V2MatchResponse` | 경기 기본 정보 (점수, 기간, 관중) |
| `MatchPuller.pull_match_event()` | `V1EventResponse` | 카드, 골, 교체 이벤트 |
| `MatchPuller.pull_match_lineup()` | `V3MatchLineupResponse` | 라인업, 교체 선수, 포메이션, 감독 |
| `MatchPuller.pull_match_official()` | `V1MatchOfficialsResponse` | 심판 정보 |

### 9.3 MatchEntity 필드 매핑

**V2MatchResponse에서**:

| API 필드 | Entity 필드 |
|---|---|
| `response.attendance` | `attendance` |
| `response.away_team.score` | `away_team_score` |
| `response.away_team.half_time_score` | `away_team_half_time_score` |
| `int(response.clock)` | `clock` |
| `fixture` entity (FK) | `fixture_id` |
| `response.home_team.score` | `home_team_score` |
| `response.home_team.half_time_score` | `home_team_half_time_score` |
| `PeriodEnum.from_string(response.period)` | `period` |

**V3MatchLineupResponse에서**:

| 파생 방식 | Entity 필드 |
|---|---|
| Captain player (lineup에서 `is_captain=True`) | `home_team_captain_id`, `away_team_captain_id` |
| Manager from lineup.managers | `home_team_manager`, `away_team_manager` (StaffEntity FK) |
| `formation.formation.split("-")` → `[int]` | `home_team_formation`, `away_team_formation` |

**V1MatchOfficialsResponse에서**:

| Official type 문자열 | Entity 필드 |
|---|---|
| `"Referee"` | `official_main_referee_id` |
| `"Assistant Referee#1"` | `official_assistant_1_referee_id` |
| `"Assistant Referee#2"` | `official_assistant_2_referee_id` |
| `"Fourth official"` | `official_fourth_referee_id` |
| `"Video Assistant Referee"` | `official_var_id` |
| `"Assistant VAR Official"` | `official_assistant_var_id` |

### 9.4 Association 테이블 매핑

**Lineup** (`match_lineup_association` via `match_repo.append_lineup`):

| 소스 | 필드 |
|---|---|
| Player entity (FK) | `player_id` |
| `PositionEnum.from_string(player.position)` | `position` |
| `int(player.shirt_num)` | `shirt_number` |
| Formation grid row/column | `row`, `column` |
| Home/Away flag | `is_home` |

**Substitute** (`match_substitute_association` via `match_repo.append_substitute`):

| 소스 | 필드 |
|---|---|
| Player entity (FK) | `player_id` |
| `PositionEnum.from_string(player.position)` | `position` |
| `int(player.shirt_num)` | `shirt_number` |
| Home/Away flag | `is_home` |

**Card** (`match_card_association` via `match_repo.append_card`):

| 소스 (`EventCardDict`) | 필드 |
|---|---|
| Player entity (by `player_id`) | `player_id` |
| Event index | `index` |
| `CardTypeEnum.from_string(card["type"])` | `card_type` |
| `int(card["time"])` | `clock` |
| Home/Away flag | `is_home` |

**Goal** (`match_goal_association` via `match_repo.append_goal`):

| 소스 (`EventGoalDict`) | 필드 |
|---|---|
| Player entity (by `player_id`) | `player_id` |
| Assist player entity (nullable) | `assist_player_id` |
| Event index | `index` |
| `goal["goalType"] == "Penalty"` | `is_penalty` |
| `goal["goalType"] == "Own"` | `is_own_goal` |
| `int(goal["time"])` | `clock` |
| Home/Away flag | `is_home` |

**Substitution** (`match_substitution_association` via `match_repo.append_substitution`):

| 소스 (`EventSubDict`) | 필드 |
|---|---|
| In player entity (by `player_on_id`) | `in_player_id` |
| Out player entity (by `player_off_id`) | `out_player_id` |
| `int(sub["time"])` | `clock` |
| Home/Away flag | `is_home` |

### 9.5 StaffEntity 생성 (Managers)

```python
# Lineup API에서 manager 정보 추출
# source_id: manager API ID
# display_name_en, display_name_kr (번역), full_name
```

### 9.6 OfficialEntity 생성

```python
# source_id: MD5(display_name_en) 기반 해시
# display_name_en, display_name_kr (번역), full_name
```

### 9.7 FULLTIME 스킵 로직

```python
existing = await match_repo.get_by_pulselive_id(fixture.source_id)
if existing and existing.period == PeriodEnum.FULLTIME:
    return existing  # 이미 완료된 경기는 다시 처리하지 않음
```

---

## 10. Step 9: MatchStatMerger 구현

### 10.1 체크리스트

- [x] `merger/mergers/match_stat.py` 구현
- [x] 경기당 2개 Entity 생성 (Home, Away)
- [x] 50+ 필드 매핑 (직접 변환 + 파생 계산)
- [x] Import 및 단위 테스트

### 10.2 API → Entity 필드 매핑 (주요)

**소스 Puller**: `MatchStatPuller.pull_match_stat()` → `list[V1MatchTeamStatResponse]`

**source_id**: `f"{match.source_id}_{team.source_id}"`

| 계산식 / API 필드 | Entity 필드 |
|---|---|
| `int(stats.big_chance_scored + stats.big_chance_missed)` | `big_chances` |
| `int(stats.big_chance_missed)` | `big_chances_missed` |
| `int(stats.corner_taken)` | `corners` |
| `stats.expected_goals` | `expected_goals` |
| `stats.expected_goals - (oppo.penalty_faced * 0.79)` | `expected_goals_non_penalty` |
| `stats.expected_goals_on_target` | `expected_goals_on_target` |
| `int(stats.outfielder_block)` | `defense_blocks` |
| `int(stats.total_clearance)` | `defense_clearances` |
| `int(stats.interception)` | `defense_interceptions` |
| `int(stats.saves)` | `defense_keeper_saves` |
| `int(stats.total_tackle)` | `defense_tackles_total` |
| `int(stats.won_tackle)` | `defense_tackles_won` |
| `int(stats.total_red_card)` | `discipline_red_cards` |
| `int(stats.total_yel_card)` | `discipline_yellow_cards` |
| `int(stats.duel_won + stats.duel_lost)` | `duels_total` |
| `int(stats.duel_won)` | `duels_won` |
| `int(stats.aerial_won + stats.aerial_lost)` | `duels_aerial_total` |
| `int(stats.aerial_won)` | `duels_aerial_won` |
| `duels_total - duels_aerial_total` | `duels_ground_total` |
| `stats.duel_won - stats.aerial_won` | `duels_ground_won` |
| `int(stats.won_contest)` | `duels_dribbles_successful` |
| `int(stats.total_contest)` | `duels_dribbles_total` |
| `int(stats.fk_foul_lost)` | `fouls_committed` |
| `int(stats.total_pass)` | `passes_total` |
| `int(stats.accurate_pass)` | `passes_accurate` |
| `int(stats.accurate_back_zone_pass)` | `passes_own_half` |
| `int(stats.accurate_fwd_zone_pass - stats.accurate_cross)` | `passes_opposition_half` |
| `int(stats.total_long_balls)` | `passes_total_long_balls` |
| `int(stats.accurate_long_balls)` | `passes_accurate_long_balls` |
| `int(stats.total_cross)` | `passes_total_crosses` |
| `int(stats.accurate_cross)` | `passes_accurate_crosses` |
| `int(stats.total_offside)` | `passes_offsides` |
| `int(stats.total_throws)` | `passes_throws` |
| `int(stats.touches_in_opp_box)` | `passes_touches_in_opposition_box` |
| `stats.possession_percentage` | `possession` |
| `int(stats.total_scoring_att)` | `shots_total` |
| `int(stats.ontarget_scoring_att)` | `shots_on_target` |
| `int(stats.shot_off_target)` | `shots_off_target` |
| `int(stats.blocked_scoring_att)` | `shots_blocked` |
| `int(stats.attempts_ibox)` | `shots_inside_box` |
| `int(stats.attempts_obox)` | `shots_outside_box` |
| `int(stats.hit_woodwork)` | `shots_hit_woodwork` |

> **주의**: `expected_goals_non_penalty` 계산에 상대팀(`oppo`)의 `penalty_faced` 값이 필요합니다. Home/Away 두 팀 데이터를 교차 참조해야 합니다.

---

## 11. Step 10: PlayerStatMerger 구현

### 11.1 체크리스트

- [x] `merger/mergers/player_stat.py` 구현
- [x] 2개 API 병렬 호출 (v1/player-details + v2/player-stats)
- [x] 직접 매핑 + 파생 필드 계산
- [x] source_id 생성: `f"{season.source_id}_{player.source_id}"`
- [x] Import 및 단위 테스트

### 11.2 API → Entity 필드 매핑

**소스 Pullers**:
- `PlayerPuller.pull_player_details()` → `V1PlayerDetailsResponse` (shirt number, current team)
- `PlayerStatPuller.pull_player_stats()` → `V2PlayerStatResponse` (전체 통계)

**직접 매핑** (주요 필드):

| API 필드 (`PlayerStatsDict`) | Entity 필드 |
|---|---|
| `shirt_num` (from v1 details) | `number` |
| `stats["appearances"]` | `appearances` |
| `stats["blockedShots"]` | `defending_blocked` |
| `stats["aerialDuels"]` | `defending_duels_aerial_total` |
| `stats["aerialDuelsWon"]` | `defending_duels_aerial_won` |
| `stats["groundDuels"]` | `defending_duels_ground_total` |
| `stats["groundDuelsWon"]` | `defending_duels_ground_won` |
| `stats["duels"]` | `defending_duels_total` |
| `stats["duelsWon"]` | `defending_duels_won` |
| `stats["totalFoulsConceded"]` | `defending_fouls_committed` |
| `stats["interceptions"]` | `defending_interceptions` |
| `stats["possessionWonFinalThird"]` | `defending_possession_won_final_third` |
| `stats["recoveries"]` | `defending_recoveries` |
| `stats["totalTackles"]` | `defending_tackles_total` |
| `stats["tacklesWon"]` | `defending_tackles_won` |
| `stats["totalRedCards"]` | `discipline_red_cards` |
| `stats["straightRedCards"]` | `discipline_red_cards_direct` |
| `stats["yellowCards"]` | `discipline_yellow_cards` |
| `stats["cleanSheets"]` | `goalkeeping_clean_sheets` |
| `stats["goalsConceded"]` | `goalkeeping_goals_conceded` |
| `stats["catches"]` | `goalkeeping_high_claim` |
| `stats["penaltiesFaced"]` | `goalkeeping_penalties_faced` |
| `stats["penaltyGoalsConceded"]` | `goalkeeping_penalty_goals_conceded` |
| `stats["savesMade"]` | `goalkeeping_saves` |
| `stats["successfulLongPasses"]` | `passing_long_balls_accurate` |
| `stats["goalAssists"]` | `passing_assists` |
| `stats["expectedAssists"]` | `passing_expected_assists` |
| `stats["totalPasses"]` | `passing_passes_total` |
| `stats["successfulCrossesAndCorners"]` | `passing_crosses_successful` |
| `stats["successfulDribbles"]` | `possession_dribble_successful` |
| `stats["totalFoulsWon"]` | `possession_fouls_won` |
| `stats["touches"]` | `possession_touches` |
| `stats["totalTouchesInOppositionBox"]` | `possession_touches_in_opposition_box` |
| `stats["expectedGoals"]` | `shooting_expected_goals` |
| `stats["expectedGoalsOnTarget"]` | `shooting_expected_goals_on_target` |
| `stats["goals"]` | `shooting_goals` |
| `stats["penaltyGoals"]` | `shooting_goals_penalty` |
| `stats["penaltiesTaken"]` | `shooting_penalties_taken` |
| `stats["shotsOnTargetIncGoals"]` | `shooting_shots_on_target` |

### 11.3 파생 필드

| 계산식 | Entity 필드 |
|---|---|
| `expectedGoalsOnTargetConceded - goalsConceded` | `goalkeeping_goals_prevented` |
| `penaltiesFaced - penaltyGoalsConceded` | `goalkeeping_penalty_saved` |
| `successfulLongPasses + unsuccessfulLongPasses` | `passing_long_balls_total` |
| `goalAssists + keyPassesAttemptAssists` | `passing_chances_created` |
| `successfulShortPasses + successfulLongPasses` | `passing_passes_successful` |
| `successfulCrossesAndCorners + unsuccessfulCrossesAndCorners` | `passing_crosses_total` |
| `successfulDribbles + unsuccessfulDribbles` | `possession_dribble_total` |
| `expectedGoals - (0.79 * penaltiesTaken)` | `shooting_expected_goals_non_penalty` |
| `totalShots + blockedShots` | `shooting_shots` |

---

## 12. Step 11: TeamStatMerger 구현

### 12.1 체크리스트

- [x] `merger/mergers/team_stat.py` 구현
- [x] **Phase 1**: DB 기반 순위표 파생 (W/D/L, 승점, 누적 승점)
- [x] **Phase 2**: API 기반 고급 통계 매핑
- [x] `TeamStatMatchAssociation` 관리
- [x] source_id 생성: `f"{season.source_id}_{team.source_id}"`
- [x] Import 및 단위 테스트

### 12.2 2-Phase 업데이트 구조

**Phase 1 — DB 파생 (순위표 데이터)**:

```python
# 각 FULLTIME 경기에서 승/무/패, 골, 승점 계산
# team_stat_repo.append_match(team_stat, match, kickoff_time) 호출
# → W/D/L, goals_for/against, points, cumulative_points 자동 업데이트
```

| 파생 방식 | Entity 필드 그룹 |
|---|---|
| 경기 결과 집계 (전체) | `overall_matches`, `overall_matches_won/drawn/lost`, `overall_goals_for/against/difference`, `overall_points` |
| 홈 경기 결과 집계 | `home_matches`, `home_matches_won/drawn/lost`, `home_goals_for/against/difference`, `home_points` |
| 원정 경기 결과 집계 | `away_matches`, `away_matches_won/drawn/lost`, `away_goals_for/against/difference`, `away_points` |
| 경기별 누적 승점 | `overall_cumulative_points`, `home_cumulative_points`, `away_cumulative_points` (ARRAY) |

**Phase 2 — API 통계**:

**소스 Puller**: `TeamStatPuller.pull_team_stats()` → `V2TeamStatsResponse`

| API 필드 (`TeamStatsDict`) | Entity 필드 (`overall_stat_*`) |
|---|---|
| `stats["cornersTakenInclShortCorners"]` | `overall_stat_attack_corners` |
| `stats["shotsOnTargetInclGoals"]` | `overall_stat_attack_shots_on_target` |
| `stats["totalShots"]` | `overall_stat_attack_total_shots` |
| `stats["touchesInOppBox"]` | `overall_stat_attack_touches_in_opposition_box` |
| `stats["expectedAssists"]` | `overall_stat_attack_expected_assists` |
| `stats["expectedGoals"]` | `overall_stat_attack_expected_goals` |
| `stats["possessionPercentage"]` | `overall_stat_average_possession` |
| `stats["blockedShots"]` | `overall_stat_defense_blocks` |
| `stats["cleanSheets"]` | `overall_stat_defense_clean_sheets` |
| `stats["totalClearances"]` | `overall_stat_defense_clearances` |
| `stats["interceptions"]` | `overall_stat_defense_interceptions` |
| `stats["penaltiesSaved"]` | `overall_stat_defense_saves_penalty` |
| `stats["timesTackled"]` | `overall_stat_defense_tackles` |
| `stats["tacklesWon"]` | `overall_stat_defense_tackles_successful` |
| `stats["totalFoulsConceded"]` | `overall_stat_discipline_fouls` |
| `stats["totalRedCards"]` | `overall_stat_discipline_red_cards` |
| `stats["straightRedCards"]` | `overall_stat_discipline_red_cards_direct` |
| `stats["yellowCards"]` | `overall_stat_discipline_yellow_cards` |
| `stats["totalPasses"]` | `overall_stat_attack_passes` |
| (파생: duels, crosses, long_balls) | 각 해당 필드 |

---

## 13. Step 12: AwardMerger 구현

### 13.1 체크리스트

- [x] `merger/mergers/award.py` 구현
- [x] AwardTypeEnum 매핑 (type 문자열 → enum)
- [x] `PlayerStatAwardAssociation` 생성 (선수 수상)
- [x] `StaffAwardAssociation` 생성 (감독 수상)
- [x] StaffEntity 생성 (감독이 DB에 없을 경우, 번역 포함)
- [x] Award 날짜 파싱 (`"YYYY-M"` 또는 `"YYYY-M-D"` → datetime)
- [x] Import 및 단위 테스트

### 13.2 API → 처리 흐름

**소스 Puller**: `AwardPuller.pull_awards()` → `V1AwardResponse`

**선수 수상 (PlayerAwardDict)**:

```
1. type 문자열 → AwardTypeEnum 매핑
2. AwardEntity get/create (source_id = MD5(type.value))
3. PlayerEntity 조회 (by source_id = award["id"])
4. PlayerStatEntity 조회 (by player + season)
5. PlayerStatAwardAssociation 추가 (date 파싱)
```

**감독 수상 (ManagerAwardDict)**:

```
1. type 문자열 → AwardTypeEnum 매핑
2. AwardEntity get/create
3. StaffEntity get/create (번역 포함: display_name_en → display_name_kr)
4. StaffAwardAssociation 추가 (date 파싱)
```

### 13.3 Award date 파싱

```python
# "2024-9" → datetime(2024, 9, 1, tzinfo=UTC)
# "2024-9-15" → datetime(2024, 9, 15, tzinfo=UTC)
parts = date_str.split("-")
year, month = int(parts[0]), int(parts[1])
day = int(parts[2]) if len(parts) > 2 else 1
```

---

## 14. Step 13: NewsMerger 구현

### 14.1 체크리스트

- [x] `merger/mergers/news.py` 구현
- [x] 웹 스크래핑: `__NEXT_DATA__` JSON + `ld+json` 메타데이터 파싱
- [x] Anthropic Claude API로 전체 기사 번역 (제목, 저자, 요약, 팀명 감지)
- [x] `NewsTeamAssociation` 생성 (감지된 팀명 매칭)
- [x] 페이지네이션 처리 (최대 5페이지)
- [x] Import 및 단위 테스트

### 14.2 소스 Pullers

| Puller 메서드 | 용도 |
|---|---|
| `NewsPuller.pull_league_feed()` | LeagueFeed에서 기사 목록 조회 |
| (httpx 직접 호출) | 기사 본문 스크래핑 (`permalink` URL) |

### 14.3 스크래핑 구조

```python
# 1. permalink URL에서 HTML 가져오기
# 2. BeautifulSoup으로 <script id="__NEXT_DATA__"> JSON 추출
# 3. <script type="application/ld+json"> 메타데이터 추출
# 4. articleBody, headline, datePublished 등 파싱
```

### 14.4 LLM 번역 구조

Anthropic Claude API에 전체 기사를 보내서:
- 제목 번역 (EN → KR)
- 저자명 번역 (EN → KR)
- 3-5 bullet 요약 생성 (EN + KR)
- 팀 약칭 감지 (short_name_en dict 제공)

**응답 모델**: `NewsTranslateResponse` (이미 Phase 2에서 정의됨)

### 14.5 API → Entity 필드 매핑

| 소스 | Entity 필드 (`NewsEntity`) |
|---|---|
| `translate_response.authors[].en` | `author_en` (list) |
| `translate_response.authors[].ko` | `author_kr` (list) |
| `" ".join(translate_response.summary.en)` | `content_en` |
| `" ".join(translate_response.summary.ko)` | `content_kr` |
| `datetime.fromisoformat(article.datePublished)` | `publish_date` |
| `content.permalink` | `url` |
| `SourceEnum.THE_ATHLETIC` | `source` |
| `content.consumable_id` | `source_id` |
| `article.thumbnailUrl` | `thumbnail_url` |
| `translate_response.title.en` | `title_en` |
| `translate_response.title.ko` | `title_kr` |
| `NewsTypeEnum.FULL_ARTICLE` | `type` |

### 14.6 Team Association 매칭

```python
# LLM이 감지한 팀명 리스트와 DB의 team.short_name_en 비교
for team_abbr in translate_response.teams:
    team = await team_repo.get_by_abbreviation(team_abbr)
    if team:
        # news_team_association 생성
```

---

## 15. Step 14: PlayerStatScorer 구현

### 15.1 체크리스트

- [x] `merger/scorer.py` 구현
- [x] 6개 카테고리 점수 계산 (0.0 ~ 100.0)
- [x] Bayesian shrinkage 구현
- [x] 포지션별 가중치 적용
- [x] Import 및 단위 테스트

### 15.2 점수 카테고리

**Archive 참조**: `archive/legacy_scripts/backfill_player_stat_scores.py`
**수식 참조**: `refactoring_docs/3_calculation_formulas_reference.md`

| 카테고리 | Entity 필드 | 주요 지표 |
|---|---|---|
| Shooting | `score_shooting` | npxG/90 (40%), non-penalty goals/90 (30%), SOT/Shots rate (20%), goals/xG ratio (10%) |
| Passing | `score_passing` | xA/90 (30%), chances/90 (20%), assists/90 (15%), pass accuracy (25%), cross+longball accuracy (10%) |
| Defending (Outfield) | `score_defending` | tackles_won/90, interceptions/90, blocked/90, recoveries/90, duel win rate, aerial win rate - fouls/90 |
| Defending (GK) | `score_defending` | saves/90 (55%), goals_prevented/90 (25%), clean_sheets/90 (20%) |
| Dribbling | `score_dribbling` | success rate (35%), volume/90 (30%), fouls won/90 (20%), box touches/90 (15%) |
| Discipline | `score_discipline` | 100 - penalty (0.7 * weighted_cards_norm + 0.3 * fouls_norm) |
| **Overall** | `score_overall` | 포지션별 가중치 blend (arithmetic + geometric mean) + Bayesian shrinkage |

### 15.3 포지션별 가중치

| Position | Shooting | Passing | Defending | Dribbling | Discipline |
|---|---|---|---|---|---|
| FW | 0.35 | 0.20 | 0.05 | 0.30 | 0.10 |
| MF | 0.20 | 0.35 | 0.15 | 0.20 | 0.10 |
| DF | 0.05 | 0.20 | 0.45 | 0.10 | 0.20 |
| GK | 0.00 | 0.10 | 0.80 | 0.00 | 0.10 |

### 15.4 Bayesian Shrinkage

```python
# Prior strength: n0 = 450 minutes (~5 matches)
# Overall prior strength: M0 = 225 minutes (~2.5 matches)
# Prior mean: 0.5 (50점)

# shrunk_score = (minutes * raw_score + n0 * prior) / (minutes + n0)
```

> **중요**: 점수 계산의 모든 공식, 가중치, 상수는 `3_calculation_formulas_reference.md`에 문서화되어 있습니다. 구현 시 반드시 참조하세요.

---

## 16. Step 15: MergerContainer 구현

### 16.1 체크리스트

- [x] `merger/container.py` 구현
- [x] dependency-injector 기반 DI Container
- [x] RepositoryContainer, PullerContainer 의존
- [x] 모든 Merger + 공통 서비스 Provider 등록
- [x] Import 및 단위 테스트

### 16.2 Provider 목록

```python
from dependency_injector import containers, providers

class MergerContainer(containers.DeclarativeContainer):
    """Merger 컴포넌트 DI Container"""

    # 외부 의존성
    config = providers.Dependency()
    repository_container = providers.DependsOn()
    puller_container = providers.DependsOn()

    # 공통 서비스
    translator_service = providers.Singleton(TranslatorService, ...)
    resource_validator = providers.Singleton(ResourceValidationClient)

    # Mergers (Factory)
    competition_merger = providers.Factory(CompetitionMerger, ...)
    season_merger = providers.Factory(SeasonMerger, ...)
    team_merger = providers.Factory(TeamMerger, ...)
    player_merger = providers.Factory(PlayerMerger, ...)
    fixture_merger = providers.Factory(FixtureMerger, ...)
    match_merger = providers.Factory(MatchMerger, ...)
    match_stat_merger = providers.Factory(MatchStatMerger, ...)
    player_stat_merger = providers.Factory(PlayerStatMerger, ...)
    team_stat_merger = providers.Factory(TeamStatMerger, ...)
    award_merger = providers.Factory(AwardMerger, ...)
    news_merger = providers.Factory(NewsMerger, ...)

    # Scorer
    player_stat_scorer = providers.Factory(PlayerStatScorer, ...)
```

### 16.3 예상 Provider 수

| 카테고리 | Provider 수 |
|----------|-------------|
| 외부 의존성 | 3 (config, repo_container, puller_container) |
| 공통 서비스 | 2 (translator, resource_validator) |
| Mergers | 11 |
| Scorer | 1 |
| **총** | **17** |

---

## 17. Step 16: 검증

### 17.1 체크리스트

- [x] Import 검증 (모든 클래스 import 성공)
- [x] MergerContainer 초기화 검증
- [x] 개별 Merger 단위 테스트
- [ ] 통합 테스트 (Puller → Merger → DB 확인)
- [x] `__init__.py` 빈 파일 확인

### 17.2 Import 검증 스크립트

```python
# 공통 서비스
from football_data_manager.merger.services.translator import TranslatorService
from football_data_manager.merger.services.resource_validator import ResourceValidationClient

# Mergers (11개)
from football_data_manager.merger.mergers.competition import CompetitionMerger
from football_data_manager.merger.mergers.season import SeasonMerger
from football_data_manager.merger.mergers.team import TeamMerger, GroundMerger
from football_data_manager.merger.mergers.player import PlayerMerger
from football_data_manager.merger.mergers.fixture import FixtureMerger
from football_data_manager.merger.mergers.match import MatchMerger
from football_data_manager.merger.mergers.match_stat import MatchStatMerger
from football_data_manager.merger.mergers.player_stat import PlayerStatMerger
from football_data_manager.merger.mergers.team_stat import TeamStatMerger
from football_data_manager.merger.mergers.award import AwardMerger
from football_data_manager.merger.mergers.news import NewsMerger

# Scorer
from football_data_manager.merger.scorer import PlayerStatScorer

# Container
from football_data_manager.merger.container import MergerContainer

print(f"All {14} classes imported successfully")
```

### 17.3 __init__.py 검증

```bash
# 모든 __init__.py가 비어있는지 확인
for f in $(find football_data_manager/merger -name "__init__.py"); do
    if [ -s "$f" ]; then
        echo "NOT EMPTY: $f"
    fi
done
```

---

## 18. 검증 체크리스트

### 18.1 구조 검증

- [x] `merger/` 디렉토리 구조 올바름 (services/, mergers/, container.py, scorer.py)
- [x] 모든 `__init__.py` 파일이 비어있음
- [x] 파일 수 18개

### 18.2 공통 서비스 검증

- [x] `TranslatorService.translate_word()` 정상 동작
- [x] `ResourceValidationClient.validate_url_exists()` 정상 동작
- [x] 캐싱 동작 확인

### 18.3 개별 Merger 검증

- [x] CompetitionMerger: 허용 ID만 처리, 번역 정상
- [x] SeasonMerger: 연도 파싱, 날짜 파생 정상
- [x] GroundMerger: source_id 해시 생성, 번역 정상
- [x] TeamMerger: badge URL 검증, 번역, Ground 연계 정상
- [x] PlayerMerger: photo/flag URL 검증, 국적 번역 캐싱 정상
- [x] FixtureMerger: Team/Ground FK 조회, UTC 변환 정상
- [x] MatchMerger: 4 API 처리, 5 Association 채우기, Staff/Official 생성 정상
- [x] MatchStatMerger: Home/Away 2개 Entity 생성, 파생 필드 계산 정상
- [x] PlayerStatMerger: 병렬 API, 파생 필드 계산 정상
- [x] TeamStatMerger: 2-Phase 업데이트, Association 관리 정상
- [x] AwardMerger: Award 타입 매핑, 2개 Association 생성 정상
- [x] NewsMerger: 스크래핑, LLM 번역, Team Association 매칭 정상

### 18.4 PlayerStatScorer 검증

- [x] 6개 카테고리 점수 0.0 ~ 100.0 범위 내
- [x] 포지션별 가중치 적용 정상
- [x] Bayesian shrinkage 적용 정상

### 18.5 MergerContainer 검증

- [x] 모든 17개 Provider 정상 초기화
- [x] 의존성 주입 체인 정상 (config → service → merger)

---

## 19. Phase 3 완료 기준

### 19.1 필수 완료

- [x] 공통 서비스 2개 구현 완료 (TranslatorService, ResourceValidationClient)
- [x] 11개 Merger 모두 구현 완료
- [x] PlayerStatScorer 구현 완료
- [x] MergerContainer 구현 완료
- [x] 모든 Import 성공
- [x] 모든 `__init__.py` 비어있음

### 19.2 품질 기준

- [x] 모든 Merger가 Check → Translate → Validate → Create/Update 패턴 준수
- [x] archive의 필드 매핑 100% 보존 (데이터 유실 없음)
- [x] 점수 계산 공식이 `3_calculation_formulas_reference.md`와 일치
- [x] 모든 Association 테이블 정상 채워짐
- [x] 번역 캐싱 패턴 적용 (불필요한 API 호출 방지)
- [x] 리소스 URL 검증 캐싱 적용

---

## 20. 다음 단계

### Phase 4: Scheduler 구현 (1주)

Phase 3 완료 후:

1. **APScheduler 설정**: AsyncIOScheduler 초기화
2. **Job 클래스 구현**: 각 Merger를 호출하는 Job 정의
3. **스케줄 설정**: Interval별 Job 매핑 (5분, 10분, 1시간, 1일, 1달)
4. **전체 통합 테스트**: Puller → Merger → DB → Scheduler 엔드투엔드

### Merger → Scheduler 연결 포인트

| Job | Merger | Interval |
|-----|--------|----------|
| LiveMatchJob | MatchMerger + MatchStatMerger | 5분 |
| FixtureUpdateJob | FixtureMerger | 10분 |
| PlayerStatsJob | PlayerStatMerger + TeamStatMerger | 1시간 |
| PlayerSyncJob | PlayerMerger + TeamMerger | 1일 |
| SeasonSetupJob | CompetitionMerger + SeasonMerger | 1달 |
| AwardSyncJob | AwardMerger | 1일 |
| NewsSyncJob | NewsMerger | 1시간 |
| ScoreSyncJob | PlayerStatScorer | 1일 |

---

**Last Updated**: 2026-02-23
**Maintained By**: @jormal
