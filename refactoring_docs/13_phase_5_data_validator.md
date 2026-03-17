# Phase 5: Data Validator 구현

**상태**: 진행 중 🔄
**목표**: `app.py`에 데이터 교차 검증 명령어 추가 (entity별 자체 정합성 + 교차 검증 + FK 검증)
**선행 조건**: Phase 4 완료 ✅

> **시작 전에**: 이 문서는 실행 가이드입니다. 전체 계획은 `1_master_plan.md`를, 검증 규칙 전체 목록은 `0_README.md`의 Phase 5 섹션을 참고하세요.

---

## 목차

1. [개요](#1-개요)
2. [Step 1: 디렉토리 구조 생성](#2-step-1-디렉토리-구조-생성)
3. [Step 2: 검증 결과 모델 구현](#3-step-2-검증-결과-모델-구현)
4. [Step 3: AbstractValidator 구현](#4-step-3-abstractvalidator-구현)
5. [Step 4: 개별 Validator 구현](#5-step-4-개별-validator-구현)
6. [Step 5: ValidationOrchestrator 구현](#6-step-5-validationorchestrator-구현)
7. [Step 6: ValidatorContainer 구현](#7-step-6-validatorcontainer-구현)
8. [Step 7: app.py validate 명령어 추가](#8-step-7-apppy-validate-명령어-추가)
9. [Step 8: 검증](#9-step-8-검증)
10. [검증 체크리스트](#10-검증-체크리스트)
11. [Phase 5 완료 기준](#11-phase-5-완료-기준)
12. [다음 단계](#12-다음-단계)

---

## 1. 개요

### 1.1 Phase 5 범위

Phase 5는 Data Validator 컴포넌트를 구현하는 단계입니다. DB에 저장된 데이터의 정합성을 검증하여 PASS/FAIL/WARNING 리포트를 출력합니다:

- **validate 명령어 추가**: `app.py validate {entity}` CLI subcommand
- **3단계 검증**: 자체 정합성 → 교차 검증 → FK 존재 검증
- **결과 리포트**: PASS/FAIL/WARNING 항목별 요약 + 상세 출력
- **선택적 실행**: 특정 entity만 검증하거나 전체 검증
- **비동기 실행**: `asyncio.run()` 기반

### 1.2 검증 레벨 정의

| 레벨 | 의미 | 예시 |
|------|------|------|
| **PASS** | 검증 통과 | `overall_matches == home + away` |
| **FAIL** | 데이터 무결성 위반 (반드시 수정 필요) | FK가 참조하는 레코드 미존재 |
| **WARNING** | 논리적 의심 (검토 필요, 허용 가능) | `PlayerStat` 없는 `PlayerChampionshipAssociation` |

### 1.3 현재 상태 (Phase 4 완료 후)

```
football_data_manager/
├── repository/                   # ✅ Phase 1 완료
│   ├── entities/                 # 15 Entity + 11 Association
│   ├── repositories/             # 15 Repository + base + pulselive
│   ├── session.py                # SessionFactory
│   └── container.py              # RepositoryContainer (17 providers)
├── puller/                       # ✅ Phase 2 완료
│   ├── interfaces/               # Pydantic Interface (TypedDict + BaseModel)
│   ├── clients/                  # HTTP / GraphQL 클라이언트
│   ├── pullers/                  # 11 Puller 구현체
│   └── container.py              # PullerContainer
├── merger/                       # ✅ Phase 3 완료
│   ├── services/                 # TranslatorService, ResourceValidationClient
│   ├── mergers/                  # 11 Merger + PlayerStatScorer
│   └── container.py              # MergerContainer
├── syncer/                       # ✅ Phase 4 완료
│   ├── tasks/                    # 11 SyncTask
│   ├── dependency.py             # DependencyResolver (DAG)
│   ├── orchestrator.py           # SyncOrchestrator
│   └── container.py              # SyncContainer
├── validator/                    # 🆕 Phase 5 (이번 단계)
│   ├── validators/               # 개별 Validator 구현체
│   ├── orchestrator.py           # ValidationOrchestrator
│   └── container.py              # ValidatorContainer
└── common/                       # 공유 유틸리티
```

### 1.4 설계 원칙

1. **읽기 전용**: Validator는 DB를 읽기만 하고 수정하지 않음
2. **독립 실행**: Sync 없이 기존 DB 데이터만으로 검증 가능
3. **점진적 검증**: entity별로 독립 실행 가능, 전체 검증도 지원
4. **명확한 리포트**: 어떤 레코드가 어떤 규칙을 위반했는지 상세 출력

---

## 2. Step 1: 디렉토리 구조 생성

### 2.1 생성할 파일 목록

```
football_data_manager/
└── validator/
    ├── __init__.py                    # 빈 파일
    ├── validators/
    │   ├── __init__.py                # 빈 파일
    │   ├── base.py                    # AbstractValidator, ValidationResult, ValidationCheck
    │   ├── team_stat.py               # TeamStatValidator
    │   ├── player_stat.py             # PlayerStatValidator
    │   ├── match.py                   # MatchValidator
    │   ├── match_stat.py              # MatchStatValidator
    │   ├── fixture.py                 # FixtureValidator
    │   ├── season.py                  # SeasonValidator
    │   ├── competition.py             # CompetitionValidator
    │   ├── player.py                  # PlayerValidator
    │   ├── analytics.py               # AnalyticsValidator
    │   ├── news.py                    # NewsValidator
    │   └── award.py                   # AwardValidator
    ├── cross_dataset.py               # CrossDatasetValidator (전체 데이터셋 교차 검증)
    ├── orchestrator.py                # ValidationOrchestrator
    └── container.py                   # ValidatorContainer
```

### 2.2 실행

```bash
mkdir -p football_data_manager/validator/validators
touch football_data_manager/validator/__init__.py
touch football_data_manager/validator/validators/__init__.py
```

---

## 3. Step 2: 검증 결과 모델 구현

### 3.1 파일: `validator/validators/base.py`

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum

from football_data_manager.repository.session import SessionFactory


class CheckLevel(StrEnum):
    """Validation check result level."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"


@dataclass
class ValidationCheck:
    """Single validation check result."""

    rule: str
    level: CheckLevel
    entity_id: str | None = None
    detail: str = ""

    @property
    def passed(self) -> bool:
        return self.level == CheckLevel.PASS


@dataclass
class ValidationResult:
    """Aggregated result for one validator execution."""

    entity: str
    checks: list[ValidationCheck] = field(default_factory=list)

    @property
    def pass_count(self) -> int:
        return sum(1 for c in self.checks if c.level == CheckLevel.PASS)

    @property
    def fail_count(self) -> int:
        return sum(1 for c in self.checks if c.level == CheckLevel.FAIL)

    @property
    def warning_count(self) -> int:
        return sum(1 for c in self.checks if c.level == CheckLevel.WARNING)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def success(self) -> bool:
        return self.fail_count == 0

    def add_pass(
        self, rule: str, entity_id: str | None = None, detail: str = ""
    ) -> None:
        self.checks.append(
            ValidationCheck(
                rule=rule, level=CheckLevel.PASS, entity_id=entity_id, detail=detail
            )
        )

    def add_fail(
        self, rule: str, entity_id: str | None = None, detail: str = ""
    ) -> None:
        self.checks.append(
            ValidationCheck(
                rule=rule, level=CheckLevel.FAIL, entity_id=entity_id, detail=detail
            )
        )

    def add_warning(
        self, rule: str, entity_id: str | None = None, detail: str = ""
    ) -> None:
        self.checks.append(
            ValidationCheck(
                rule=rule,
                level=CheckLevel.WARNING,
                entity_id=entity_id,
                detail=detail,
            )
        )


class AbstractValidator(ABC):
    """Base class for all validators."""

    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory

    @abstractmethod
    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        """Execute validation checks and return result."""
        raise NotImplementedError
```

### 3.2 설계 포인트

- `ValidationCheck`: 개별 검증 규칙의 결과 (규칙명, 레벨, 대상 entity ID, 상세 메시지)
- `ValidationResult`: Validator 하나의 전체 결과 (entity명, check 목록, 집계 property)
- `AbstractValidator`: 모든 Validator의 베이스. `session_factory`만 주입받아 DB 읽기 수행
- `season_id`, `competition_id` 파라미터: 특정 시즌/대회로 범위 제한 가능

---

## 4. Step 3: AbstractValidator 구현

Step 2에서 이미 `AbstractValidator`를 정의했습니다. 추가적으로 공통 헬퍼 메서드를 제공합니다.

### 4.1 공통 헬퍼 메서드 (base.py에 추가)

```python
class AbstractValidator(ABC):
    """Base class for all validators."""

    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory

    @abstractmethod
    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        raise NotImplementedError

    # --- 공통 헬퍼 ---

    @staticmethod
    def check_equal(
        result: ValidationResult,
        rule: str,
        actual: int | float,
        expected: int | float,
        entity_id: str | None = None,
        tolerance: float = 0.0,
    ) -> None:
        """값이 같은지 검증. tolerance > 0이면 근사 비교."""
        if abs(actual - expected) <= tolerance:
            result.add_pass(rule, entity_id)
        else:
            result.add_fail(
                rule, entity_id,
                detail=f"expected={expected}, actual={actual}",
            )

    @staticmethod
    def check_lte(
        result: ValidationResult,
        rule: str,
        smaller: int | float | None,
        larger: int | float | None,
        entity_id: str | None = None,
    ) -> None:
        """smaller <= larger 검증. None이면 스킵."""
        if smaller is None or larger is None:
            return
        if smaller <= larger:
            result.add_pass(rule, entity_id)
        else:
            result.add_fail(
                rule, entity_id,
                detail=f"{smaller} > {larger}",
            )

    @staticmethod
    def check_range(
        result: ValidationResult,
        rule: str,
        value: int | float | None,
        low: int | float,
        high: int | float,
        entity_id: str | None = None,
    ) -> None:
        """value가 [low, high] 범위 내인지 검증. None이면 스킵."""
        if value is None:
            return
        if low <= value <= high:
            result.add_pass(rule, entity_id)
        else:
            result.add_fail(
                rule, entity_id,
                detail=f"{value} not in [{low}, {high}]",
            )

    @staticmethod
    def check_non_negative(
        result: ValidationResult,
        rule: str,
        value: int | float | None,
        entity_id: str | None = None,
    ) -> None:
        """value >= 0 검증. None이면 스킵."""
        if value is None:
            return
        if value >= 0:
            result.add_pass(rule, entity_id)
        else:
            result.add_fail(
                rule, entity_id,
                detail=f"negative value: {value}",
            )

    @staticmethod
    def check_not_empty(
        result: ValidationResult,
        rule: str,
        value: str | list | None,
        entity_id: str | None = None,
    ) -> None:
        """비어 있지 않은지 검증."""
        if value and len(value) > 0:
            result.add_pass(rule, entity_id)
        else:
            result.add_fail(rule, entity_id, detail="empty or None")

    @staticmethod
    def check_fk_exists(
        result: ValidationResult,
        rule: str,
        fk_value: str | None,
        existing_ids: set[str],
        entity_id: str | None = None,
    ) -> None:
        """FK가 참조하는 레코드가 존재하는지 검증. None이면 스킵."""
        if fk_value is None:
            return
        if fk_value in existing_ids:
            result.add_pass(rule, entity_id)
        else:
            result.add_fail(
                rule, entity_id,
                detail=f"referenced id '{fk_value}' not found",
            )
```

---

## 5. Step 4: 개별 Validator 구현

### 5.1 구현 순서 및 복잡도

검증 규칙의 상세 목록은 `0_README.md`의 Phase 5 섹션(5-1 ~ 5-12)을 참고하세요.

| 순서 | Validator | 복잡도 | 검증 유형 | 비고 |
|------|-----------|--------|-----------|------|
| 1 | CompetitionValidator | 낮음 | 자체 + FK | 기본 필드 검증 |
| 2 | SeasonValidator | 낮음 | 자체 + 교차 + FK | date 범위 검증 |
| 3 | PlayerValidator | 낮음 | 자체 + 교차 + FK | 기본 필드 + Association |
| 4 | FixtureValidator | 중간 | 자체 + 교차 + FK | Season/Match 교차 |
| 5 | MatchValidator | 높음 | 자체 + 교차(4종) + FK(12개) | Lineup/Goal/Card/Sub 교차 |
| 6 | MatchStatValidator | 중간 | 자체 + 교차 + FK | Match 쌍 검증 |
| 7 | TeamStatValidator | 높음 | 자체(30+) + 교차(13+) + FK | 가장 많은 규칙 |
| 8 | PlayerStatValidator | 높음 | 자체(30+) + 교차 + FK | 6개 카테고리별 검증 |
| 9 | AnalyticsValidator | 중간 | 자체 + 파생 재계산 + FK | 파생 필드 검증 |
| 10 | NewsValidator | 낮음 | 자체 + FK | 필드 존재 검증 |
| 11 | AwardValidator | 낮음 | 자체 + 교차 + FK | Association 검증 |
| 12 | CrossDatasetValidator | 높음 | 전체 교차 | 시즌 단위 통계 대칭 |

### 5.2 Validator 구현 패턴 (예시: TeamStatValidator)

```python
# validator/validators/team_stat.py
import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from football_data_manager.repository.entities.team_stats import TeamStatEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.match_stats import MatchStatEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.session import SessionFactory
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class TeamStatValidator(AbstractValidator):
    """TeamStat entity 검증.

    검증 규칙 참조: 0_README.md Phase 5 섹션 5-1.
    """

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory)

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="team-stat")

        async with self._session_factory.session() as session:
            # 대상 TeamStat 로드
            stmt = select(TeamStatEntity)
            if season_id:
                stmt = stmt.where(TeamStatEntity.season_id == season_id)
            team_stats = (await session.execute(stmt)).scalars().all()

            if not team_stats:
                result.add_warning("data_exists", detail="No TeamStat records found")
                return result

            # FK 참조 대상 ID 셋 로드 (한 번만)
            team_ids = set(
                row[0]
                for row in (
                    await session.execute(select(TeamEntity.id))
                ).all()
            )
            season_ids = set(
                row[0]
                for row in (
                    await session.execute(select(SeasonEntity.id))
                ).all()
            )

            for ts in team_stats:
                eid = ts.id
                self._check_self_consistency(result, ts, eid)
                self._check_stat_fields(result, ts, eid)
                self._check_fk(result, ts, eid, team_ids, season_ids)

            # 교차 검증 (MatchStat 기반)은 별도 메서드
            await self._check_cross_match_stat(result, team_stats, session)

        return result

    def _check_self_consistency(
        self, result: ValidationResult, ts: TeamStatEntity, eid: str
    ) -> None:
        """자체 정합성: 경기 수, 골, 포인트, 누적 포인트 등."""

        # overall_matches == won + drawn + lost
        self.check_equal(
            result,
            "overall_matches == won + drawn + lost",
            ts.overall_matches or 0,
            (ts.overall_matches_won or 0)
            + (ts.overall_matches_drawn or 0)
            + (ts.overall_matches_lost or 0),
            entity_id=eid,
        )

        # overall_matches == home + away
        self.check_equal(
            result,
            "overall_matches == home + away",
            ts.overall_matches or 0,
            (ts.home_matches or 0) + (ts.away_matches or 0),
            entity_id=eid,
        )

        # overall_goals_difference == goals_for - goals_against
        self.check_equal(
            result,
            "overall_goals_difference == for - against",
            ts.overall_goals_difference or 0,
            (ts.overall_goals_for or 0) - (ts.overall_goals_against or 0),
            entity_id=eid,
        )

        # overall_points == 3 * won + 1 * drawn
        self.check_equal(
            result,
            "overall_points == 3*won + 1*drawn",
            ts.overall_points or 0,
            3 * (ts.overall_matches_won or 0) + 1 * (ts.overall_matches_drawn or 0),
            entity_id=eid,
        )

        # cumulative_points[-1] == overall_points
        if ts.overall_cumulative_points and len(ts.overall_cumulative_points) > 0:
            self.check_equal(
                result,
                "cumulative_points[-1] == overall_points",
                ts.overall_cumulative_points[-1],
                ts.overall_points or 0,
                entity_id=eid,
            )

        # ... 나머지 규칙은 0_README.md 5-1 참조하여 동일 패턴으로 구현

    def _check_stat_fields(
        self, result: ValidationResult, ts: TeamStatEntity, eid: str
    ) -> None:
        """공격/수비/규율 통계 필드 정합성."""

        # passes_successful <= passes
        self.check_lte(
            result,
            "attack_passes_successful <= attack_passes",
            ts.overall_stat_attack_passes_successful,
            ts.overall_stat_attack_passes,
            entity_id=eid,
        )

        # duels_won <= duels_total
        self.check_lte(
            result,
            "defense_duels_won <= defense_duels_total",
            ts.overall_stat_defense_duels_won,
            ts.overall_stat_defense_duels_total,
            entity_id=eid,
        )

        # possession 범위
        self.check_range(
            result,
            "average_possession in [0, 100]",
            ts.overall_stat_average_possession,
            0.0,
            100.0,
            entity_id=eid,
        )

        # ... 나머지 규칙은 0_README.md 5-1 참조

    def _check_fk(
        self,
        result: ValidationResult,
        ts: TeamStatEntity,
        eid: str,
        team_ids: set[str],
        season_ids: set[str],
    ) -> None:
        """FK 존재 검증."""
        self.check_fk_exists(result, "team_id FK", ts.team_id, team_ids, eid)
        self.check_fk_exists(result, "season_id FK", ts.season_id, season_ids, eid)

    async def _check_cross_match_stat(
        self,
        result: ValidationResult,
        team_stats: list[TeamStatEntity],
        session,
    ) -> None:
        """교차 검증: TeamStat ↔ Match/MatchStat."""
        # 구현 시 MatchStat 집계와 TeamStat 필드를 비교
        # 상세 규칙: 0_README.md 5-1 "교차 검증 (TeamStat ↔ Match/MatchStat)" 참조
        pass
```

### 5.3 Validator 구현 패턴 (예시: MatchValidator 요약)

```python
# validator/validators/match.py
class MatchValidator(AbstractValidator):
    """Match entity 검증.

    검증 규칙 참조: 0_README.md Phase 5 섹션 5-3.
    """

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="match")

        async with self._session_factory.session() as session:
            # Match 로드 (Association eager load)
            stmt = select(MatchEntity).options(
                selectinload(MatchEntity.lineup_associations),
                selectinload(MatchEntity.goal_associations),
                selectinload(MatchEntity.card_associations),
                selectinload(MatchEntity.substitution_associations),
            )
            matches = (await session.execute(stmt)).scalars().all()

            for match in matches:
                eid = match.id
                self._check_self_consistency(result, match, eid)
                self._check_lineup(result, match, eid)
                self._check_goals(result, match, eid)
                self._check_cards(result, match, eid)
                self._check_substitutions(result, match, eid)
                self._check_fk(result, match, eid, session)

        return result
```

### 5.4 CrossDatasetValidator 구현 패턴

```python
# validator/cross_dataset.py
class CrossDatasetValidator(AbstractValidator):
    """전체 데이터셋 교차 검증.

    검증 규칙 참조: 0_README.md Phase 5 섹션 5-12.
    """

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="cross-dataset")

        async with self._session_factory.session() as session:
            await self._check_season_symmetry(result, session, season_id)
            await self._check_source_id_uniqueness(result, session)
            await self._check_orphan_records(result, session)

        return result

    async def _check_season_symmetry(
        self, result: ValidationResult, session, season_id: str | None
    ) -> None:
        """시즌 단위 통계 대칭 검증.

        - 총 goals_for 합 == 총 goals_against 합
        - 총 matches_won 합 == 총 matches_lost 합
        - matches_drawn 합이 짝수
        - Fixture 수 == 팀수 * (팀수 - 1)
        """
        pass

    async def _check_source_id_uniqueness(
        self, result: ValidationResult, session
    ) -> None:
        """각 entity 타입별 source_id 중복 검증."""
        pass

    async def _check_orphan_records(
        self, result: ValidationResult, session
    ) -> None:
        """FK가 참조하는 parent 레코드 존재 여부, 고아 레코드 검출."""
        pass
```

---

## 6. Step 5: ValidationOrchestrator 구현

### 6.1 파일: `validator/orchestrator.py`

Syncer의 `SyncOrchestrator`와 유사한 패턴으로, 선택된 entity의 Validator를 순서대로 실행합니다.

```python
# validator/orchestrator.py
import logging
from enum import StrEnum

from football_data_manager.validator.container import ValidatorContainer
from football_data_manager.validator.validators.base import (
    CheckLevel,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class ValidateEntity(StrEnum):
    """Supported validate targets."""

    COMPETITION = "competition"
    SEASON = "season"
    TEAM_STAT = "team-stat"
    PLAYER_STAT = "player-stat"
    MATCH = "match"
    MATCH_STAT = "match-stat"
    FIXTURE = "fixture"
    PLAYER = "player"
    ANALYTICS = "analytics"
    NEWS = "news"
    AWARD = "award"
    CROSS_DATASET = "cross-dataset"


# 검증 실행 순서 (독립적이므로 순서 큰 의미 없으나, 간단한 것부터)
VALIDATE_ORDER: list[ValidateEntity] = [
    ValidateEntity.COMPETITION,
    ValidateEntity.SEASON,
    ValidateEntity.PLAYER,
    ValidateEntity.FIXTURE,
    ValidateEntity.MATCH,
    ValidateEntity.MATCH_STAT,
    ValidateEntity.TEAM_STAT,
    ValidateEntity.PLAYER_STAT,
    ValidateEntity.ANALYTICS,
    ValidateEntity.NEWS,
    ValidateEntity.AWARD,
    ValidateEntity.CROSS_DATASET,
]


class ValidationOrchestrator:
    """Orchestrate validators and collect results."""

    def __init__(self, container: ValidatorContainer):
        self._container = container

    async def validate(
        self,
        target: ValidateEntity,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> list[ValidationResult]:
        """Run a single entity validator."""
        validator = self._container.create_validator(target)
        result = await validator.validate(
            season_id=season_id, competition_id=competition_id
        )
        return [result]

    async def validate_all(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> list[ValidationResult]:
        """Run all validators in order."""
        results: list[ValidationResult] = []
        total = len(VALIDATE_ORDER)

        for idx, entity in enumerate(VALIDATE_ORDER, 1):
            logger.info("[%d/%d] Validating %s ...", idx, total, entity.value)
            try:
                validator = self._container.create_validator(entity)
                result = await validator.validate(
                    season_id=season_id, competition_id=competition_id
                )
            except Exception as error:
                logger.exception("Validation failed for %s", entity.value)
                result = ValidationResult(entity=entity.value)
                result.add_fail("validator_execution", detail=str(error))

            results.append(result)
            logger.info(
                "[%d/%d] Finished %s: PASS=%d, FAIL=%d, WARNING=%d",
                idx, total, entity.value,
                result.pass_count, result.fail_count, result.warning_count,
            )

        return results

    @staticmethod
    def print_summary(results: list[ValidationResult]) -> None:
        """Print summary table for validation results."""
        headers = ["Entity", "Total", "PASS", "FAIL", "WARNING", "Status"]
        widths = [15, 6, 6, 6, 8, 8]

        def _line(parts: list[str]) -> str:
            return " | ".join(
                part.ljust(width) for part, width in zip(parts, widths, strict=False)
            )

        print(_line(headers))
        print("-" * (sum(widths) + 3 * (len(widths) - 1)))

        for result in results:
            status = "OK" if result.success else "FAIL"
            print(
                _line([
                    result.entity,
                    str(result.total),
                    str(result.pass_count),
                    str(result.fail_count),
                    str(result.warning_count),
                    status,
                ])
            )

        print("-" * (sum(widths) + 3 * (len(widths) - 1)))

        total_pass = sum(r.pass_count for r in results)
        total_fail = sum(r.fail_count for r in results)
        total_warn = sum(r.warning_count for r in results)
        total_all = sum(r.total for r in results)
        overall = "OK" if all(r.success for r in results) else "FAIL"

        print(
            _line([
                "Total",
                str(total_all),
                str(total_pass),
                str(total_fail),
                str(total_warn),
                overall,
            ])
        )

    @staticmethod
    def print_detail(results: list[ValidationResult], level: CheckLevel | None = None) -> None:
        """Print detailed check results, optionally filtered by level."""
        for result in results:
            failures = [
                c for c in result.checks
                if level is None or c.level == level
            ]
            if not failures:
                continue

            print(f"\n=== {result.entity} ===")
            for check in failures:
                prefix = f"[{check.level}]"
                eid = f" ({check.entity_id})" if check.entity_id else ""
                detail = f" - {check.detail}" if check.detail else ""
                print(f"  {prefix} {check.rule}{eid}{detail}")
```

### 6.2 출력 예시

```
Entity          | Total  | PASS   | FAIL   | WARNING  | Status
---------------------------------------------------------------------------
competition     | 21     | 21     | 0      | 0        | OK
season          | 14     | 13     | 0      | 1        | OK
team-stat       | 680    | 675    | 3      | 2        | FAIL
player-stat     | 1240   | 1238   | 0      | 2        | OK
...
---------------------------------------------------------------------------
Total           | 4280   | 4260   | 3      | 17       | FAIL

=== team-stat (FAIL details) ===
  [FAIL] overall_matches == won + drawn + lost (ts_abc123) - expected=38, actual=37
  [FAIL] team_id FK (ts_def456) - referenced id 'tm_999' not found
  [FAIL] overall_points == 3*won + 1*drawn (ts_abc123) - expected=72, actual=71
```

---

## 7. Step 6: ValidatorContainer 구현

### 7.1 파일: `validator/container.py`

```python
# validator/container.py
from pathlib import Path

from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.common.utils.constants import CONFIG_PATH
from football_data_manager.repository.container import RepositoryContainer
from football_data_manager.repository.session import SessionFactory
from football_data_manager.validator.orchestrator import ValidateEntity
from football_data_manager.validator.validators.award import AwardValidator
from football_data_manager.validator.validators.analytics import AnalyticsValidator
from football_data_manager.validator.validators.base import AbstractValidator
from football_data_manager.validator.validators.competition import CompetitionValidator
from football_data_manager.validator.validators.fixture import FixtureValidator
from football_data_manager.validator.validators.match import MatchValidator
from football_data_manager.validator.validators.match_stat import MatchStatValidator
from football_data_manager.validator.validators.news import NewsValidator
from football_data_manager.validator.validators.player import PlayerValidator
from football_data_manager.validator.validators.player_stat import PlayerStatValidator
from football_data_manager.validator.validators.season import SeasonValidator
from football_data_manager.validator.validators.team_stat import TeamStatValidator
from football_data_manager.validator.cross_dataset import CrossDatasetValidator


class ValidatorContainer:
    """DI container for validation layer."""

    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory

    def create_validator(self, entity: ValidateEntity) -> AbstractValidator:
        """Create validator instance for the given entity."""
        builders: dict[ValidateEntity, type[AbstractValidator]] = {
            ValidateEntity.COMPETITION: CompetitionValidator,
            ValidateEntity.SEASON: SeasonValidator,
            ValidateEntity.PLAYER: PlayerValidator,
            ValidateEntity.FIXTURE: FixtureValidator,
            ValidateEntity.MATCH: MatchValidator,
            ValidateEntity.MATCH_STAT: MatchStatValidator,
            ValidateEntity.TEAM_STAT: TeamStatValidator,
            ValidateEntity.PLAYER_STAT: PlayerStatValidator,
            ValidateEntity.ANALYTICS: AnalyticsValidator,
            ValidateEntity.NEWS: NewsValidator,
            ValidateEntity.AWARD: AwardValidator,
            ValidateEntity.CROSS_DATASET: CrossDatasetValidator,
        }
        validator_cls = builders[entity]
        return validator_cls(session_factory=self._session_factory)


async def create_validator_container(
    config_path: Path = CONFIG_PATH,
) -> ValidatorContainer:
    """Build validator container with DB session factory."""
    config_service = ConfigService(config_path)
    repo_container = RepositoryContainer(config_service=config_service)
    session_factory = repo_container.session_factory()
    return ValidatorContainer(session_factory=session_factory)
```

### 7.2 설계 포인트

- Validator는 DB 읽기만 하므로 Puller/Merger 의존성 없음
- `RepositoryContainer`에서 `SessionFactory`만 가져와 사용
- `dependency-injector` 대신 단순한 팩토리 패턴 사용 (Validator는 경량)
- 필요 시 `dependency-injector`로 변경 가능

---

## 8. Step 7: app.py validate 명령어 추가

### 8.1 app.py에 추가할 코드

```python
# app.py에 추가

async def validate_data(
    entity: str,
    season_id: str | None,
    competition_id: str | None,
    show_detail: bool,
    detail_level: str | None,
) -> int:
    from football_data_manager.validator.container import create_validator_container
    from football_data_manager.validator.orchestrator import (
        ValidateEntity,
        ValidationOrchestrator,
    )
    from football_data_manager.validator.validators.base import CheckLevel

    container = await create_validator_container()
    orchestrator = ValidationOrchestrator(container)

    if entity == "all":
        results = await orchestrator.validate_all(
            season_id=season_id,
            competition_id=competition_id,
        )
    else:
        results = await orchestrator.validate(
            target=ValidateEntity(entity),
            season_id=season_id,
            competition_id=competition_id,
        )

    orchestrator.print_summary(results)

    if show_detail:
        level = CheckLevel(detail_level) if detail_level else None
        orchestrator.print_detail(results, level=level)

    return 0 if all(r.success for r in results) else 1
```

### 8.2 argparse 추가

```python
# main() 함수 내 subparsers 블록에 추가

# Validate command
validate_parser = subparsers.add_parser(
    "validate",
    help="Validate data integrity across entities",
)
validate_parser.add_argument(
    "entity",
    choices=[
        "competition",
        "season",
        "team-stat",
        "player-stat",
        "match",
        "match-stat",
        "fixture",
        "player",
        "analytics",
        "news",
        "award",
        "cross-dataset",
        "all",
    ],
    help="Target entity to validate",
)
validate_parser.add_argument(
    "--season-id",
    help="Limit validation to specific season (DB id)",
)
validate_parser.add_argument(
    "--competition-id",
    help="Limit validation to specific competition (DB id)",
)
validate_parser.add_argument(
    "--detail",
    action="store_true",
    help="Show detailed check results",
)
validate_parser.add_argument(
    "--detail-level",
    choices=["PASS", "FAIL", "WARNING"],
    help="Filter detail output by check level (default: show all)",
)
```

### 8.3 라우팅 추가

```python
# main() 함수 내 라우팅 블록에 추가

elif args.command == "validate":
    try:
        return asyncio.run(
            validate_data(
                entity=args.entity,
                season_id=args.season_id,
                competition_id=args.competition_id,
                show_detail=args.detail,
                detail_level=args.detail_level,
            )
        )
    except ValueError as error:
        print(f"Error: {error}")
        return 1
```

### 8.4 CLI 사용 예시

```bash
# 특정 entity 검증
python app.py validate team-stat --season-id abc123
python app.py validate match --detail
python app.py validate player-stat --detail --detail-level FAIL

# 전체 검증
python app.py validate all
python app.py validate all --season-id abc123 --detail

# 전체 교차 검증만
python app.py validate cross-dataset --season-id abc123
```

---

## 9. Step 8: 검증

### 9.1 단위 테스트 구조

```
tests/
└── validator/
    ├── __init__.py
    ├── test_base.py                   # ValidationResult, ValidationCheck 테스트
    ├── test_team_stat_validator.py     # TeamStatValidator 테스트
    ├── test_player_stat_validator.py   # PlayerStatValidator 테스트
    ├── test_match_validator.py         # MatchValidator 테스트
    ├── test_match_stat_validator.py    # MatchStatValidator 테스트
    ├── test_orchestrator.py           # ValidationOrchestrator 테스트
    └── test_cross_dataset.py          # CrossDatasetValidator 테스트
```

### 9.2 테스트 전략

- **단위 테스트**: 각 Validator의 헬퍼 메서드와 검증 로직을 mock된 entity로 테스트
- **결과 모델 테스트**: `ValidationResult`의 집계 property (pass_count, fail_count 등)
- **통합 테스트**: 실제 DB 연결하여 검증 실행 (별도 환경)

### 9.3 테스트 예시

```python
# tests/validator/test_base.py
from football_data_manager.validator.validators.base import (
    CheckLevel,
    ValidationCheck,
    ValidationResult,
)


def test_validation_result_counts():
    result = ValidationResult(entity="test")
    result.add_pass("rule_1")
    result.add_pass("rule_2")
    result.add_fail("rule_3", detail="mismatch")
    result.add_warning("rule_4")

    assert result.pass_count == 2
    assert result.fail_count == 1
    assert result.warning_count == 1
    assert result.total == 4
    assert result.success is False


def test_validation_result_success():
    result = ValidationResult(entity="test")
    result.add_pass("rule_1")
    result.add_warning("rule_2")

    assert result.success is True  # WARNING은 success에 영향 없음


def test_check_equal_pass():
    result = ValidationResult(entity="test")
    from football_data_manager.validator.validators.base import AbstractValidator

    # check_equal은 staticmethod이므로 직접 호출
    AbstractValidator.check_equal(result, "test_rule", 10, 10)
    assert result.pass_count == 1


def test_check_equal_fail():
    result = ValidationResult(entity="test")
    from football_data_manager.validator.validators.base import AbstractValidator

    AbstractValidator.check_equal(result, "test_rule", 10, 11)
    assert result.fail_count == 1
    assert "expected=11" in result.checks[0].detail
```

---

## 10. 검증 체크리스트

### Step 1: 디렉토리 구조

- [x] `validator/` 디렉토리 생성
- [x] `validator/validators/` 디렉토리 생성
- [x] `__init__.py` 파일 생성 (빈 파일)

### Step 2: 검증 결과 모델

- [x] `CheckLevel` enum (PASS, FAIL, WARNING) 구현
- [x] `ValidationCheck` dataclass 구현
- [x] `ValidationResult` dataclass 구현 (집계 property 포함)
- [x] `AbstractValidator` ABC 구현 (session_factory 주입)
- [x] 공통 헬퍼 메서드 구현 (check_equal, check_lte, check_range, check_fk_exists 등)

### Step 3-4: 개별 Validator

- [x] CompetitionValidator 구현 (자체 + FK)
- [x] SeasonValidator 구현 (자체 + 교차 + FK)
- [x] PlayerValidator 구현 (자체 + 교차 + FK)
- [x] FixtureValidator 구현 (자체 + 교차 + FK)
- [x] MatchValidator 구현 (자체 + 교차 4종 + FK 12개)
- [x] MatchStatValidator 구현 (자체 + 교차 + FK)
- [x] TeamStatValidator 구현 (자체 30+ + 교차 13+ + FK)
- [x] PlayerStatValidator 구현 (자체 30+ + 교차 + FK)
- [x] AnalyticsValidator 구현 (자체 + 파생 재계산 + FK)
- [x] NewsValidator 구현 (자체 + FK)
- [x] AwardValidator 구현 (자체 + 교차 + FK)
- [x] CrossDatasetValidator 구현 (전체 교차)

### Step 5: Orchestrator

- [x] `ValidateEntity` enum 구현
- [x] `ValidationOrchestrator.validate()` (단일 entity)
- [x] `ValidationOrchestrator.validate_all()` (전체)
- [x] `print_summary()` 요약 테이블 출력
- [x] `print_detail()` 상세 결과 출력

### Step 6: Container

- [x] `ValidatorContainer` 구현
- [x] `create_validator_container()` 팩토리 함수

### Step 7: app.py

- [x] `validate` subcommand 추가 (argparse)
- [x] `validate_data()` async 함수 구현
- [x] 라우팅 연결
- [x] `--detail`, `--detail-level` 옵션

### Step 8: 테스트

- [x] `test_base.py`: 결과 모델 + 헬퍼 메서드 테스트
- [ ] 각 Validator별 단위 테스트
- [x] Orchestrator 테스트
- [ ] 통합 테스트 (실제 DB)

---

## 11. Phase 5 완료 기준

### 필수 (구현 완료)

- [x] 12개 Validator 구현 (11 entity + 1 cross-dataset)
- [x] `0_README.md` 5-1 ~ 5-12의 모든 검증 규칙 구현
- [x] `app.py validate` CLI 명령어 동작
- [ ] 단위 테스트 전체 통과 (`pytest tests/validator/`)
- [x] 요약 + 상세 리포트 출력

### 선택 (통합 검증)

- [ ] 실제 DB 대상 검증 실행 (통합 테스트)
- [ ] 검증 결과 기반 데이터 이상 리포트 생성
- [ ] 성능 최적화 (대량 데이터 배치 처리)

---

## 12. 다음 단계

Phase 5 완료 후:

- **Phase 6: Scheduler 구현**
  - APScheduler 설정
  - Job 클래스 구현 (sync + validate 주기적 실행)
  - 전체 통합 테스트

---

## 부록: 검증 규칙 빠른 참조

검증 규칙의 **전체 상세 목록**은 `0_README.md`의 Phase 5 섹션(5-1 ~ 5-12)에 정의되어 있습니다. 아래는 규칙 수 요약입니다:

| Entity | 자체 정합성 | 교차 검증 | FK 검증 | 합계(약) |
|--------|-----------|-----------|---------|---------|
| TeamStat (5-1) | 30+ | 13+ | 4 | ~50 |
| PlayerStat (5-2) | 30+ | 3 | 3 | ~36 |
| Match (5-3) | 10+ | 15+ | 12 | ~37 |
| MatchStat (5-4) | 20+ | 3 | 2 | ~25 |
| Fixture (5-5) | 3 | 4+ | 4 | ~11 |
| Season (5-6) | 4 | 3 | 1 | ~8 |
| Competition (5-7) | 3 | 1 | 0 | ~4 |
| Player (5-8) | 7 | 2 | 0 | ~9 |
| Analytics (5-9) | 3 | 8 | 1 | ~12 |
| News (5-10) | 12 | 1 | 0 | ~13 |
| Award (5-11) | 1 | 3 | 0 | ~4 |
| CrossDataset (5-12) | - | 5+ | - | ~5 |
| **합계** | | | | **~214** |

---

**Last Updated**: 2026-03-17
**Maintained By**: @jormal
