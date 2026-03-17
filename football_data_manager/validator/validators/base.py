from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum

from sqlalchemy import Double, Float, Integer, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.session import SessionFactory


class CheckLevel(StrEnum):
    """Validation check result level."""

    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    SKIP = "SKIP"


@dataclass(slots=True)
class ValidationCheck:
    """Single validation check result."""

    rule: str
    level: CheckLevel
    entity_id: str | None = None
    detail: str = ""

    @property
    def passed(self) -> bool:
        return self.level == CheckLevel.PASS


@dataclass(slots=True)
class ValidationResult:
    """Aggregated result for one validator execution."""

    entity: str
    checks: list[ValidationCheck] = field(default_factory=list)

    @property
    def pass_count(self) -> int:
        return sum(1 for check in self.checks if check.level == CheckLevel.PASS)

    @property
    def fail_count(self) -> int:
        return sum(1 for check in self.checks if check.level == CheckLevel.FAIL)

    @property
    def warning_count(self) -> int:
        return sum(1 for check in self.checks if check.level == CheckLevel.WARNING)

    @property
    def skip_count(self) -> int:
        return sum(1 for check in self.checks if check.level == CheckLevel.SKIP)

    @property
    def total(self) -> int:
        return len(self.checks)

    @property
    def success(self) -> bool:
        return self.fail_count == 0

    def add_pass(
        self,
        rule: str,
        entity_id: str | None = None,
        detail: str = "",
    ) -> None:
        self.checks.append(
            ValidationCheck(
                rule=rule,
                level=CheckLevel.PASS,
                entity_id=entity_id,
                detail=detail,
            )
        )

    def add_fail(
        self,
        rule: str,
        entity_id: str | None = None,
        detail: str = "",
    ) -> None:
        self.checks.append(
            ValidationCheck(
                rule=rule,
                level=CheckLevel.FAIL,
                entity_id=entity_id,
                detail=detail,
            )
        )

    def add_warning(
        self,
        rule: str,
        entity_id: str | None = None,
        detail: str = "",
    ) -> None:
        self.checks.append(
            ValidationCheck(
                rule=rule,
                level=CheckLevel.WARNING,
                entity_id=entity_id,
                detail=detail,
            )
        )

    def add_skip(
        self,
        rule: str,
        entity_id: str | None = None,
        detail: str = "",
    ) -> None:
        self.checks.append(
            ValidationCheck(
                rule=rule,
                level=CheckLevel.SKIP,
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

    @staticmethod
    def check_equal(
        result: ValidationResult,
        rule: str,
        actual: int | float,
        expected: int | float,
        entity_id: str | None = None,
        tolerance: float = 0.0,
    ) -> None:
        """Validate equality, optionally using tolerance."""
        if abs(actual - expected) <= tolerance:
            result.add_pass(rule, entity_id)
            return
        result.add_fail(
            rule,
            entity_id,
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
        """Validate smaller <= larger, skipping when either side is None."""
        if smaller is None or larger is None:
            return
        if smaller <= larger:
            result.add_pass(rule, entity_id)
            return
        result.add_fail(rule, entity_id, detail=f"{smaller} > {larger}")

    @staticmethod
    def check_range(
        result: ValidationResult,
        rule: str,
        value: int | float | None,
        low: int | float,
        high: int | float,
        entity_id: str | None = None,
    ) -> None:
        """Validate value is within inclusive range."""
        if value is None:
            return
        if low <= value <= high:
            result.add_pass(rule, entity_id)
            return
        result.add_fail(
            rule,
            entity_id,
            detail=f"{value} not in [{low}, {high}]",
        )

    @staticmethod
    def check_non_negative(
        result: ValidationResult,
        rule: str,
        value: int | float | None,
        entity_id: str | None = None,
    ) -> None:
        """Validate value is non-negative."""
        if value is None:
            return
        if value >= 0:
            result.add_pass(rule, entity_id)
            return
        result.add_fail(rule, entity_id, detail=f"negative value: {value}")

    @staticmethod
    def check_positive(
        result: ValidationResult,
        rule: str,
        value: int | float | None,
        entity_id: str | None = None,
    ) -> None:
        """Validate value is strictly positive."""
        if value is None:
            return
        if value > 0:
            result.add_pass(rule, entity_id)
            return
        result.add_fail(rule, entity_id, detail=f"non-positive value: {value}")

    @staticmethod
    def check_not_empty(
        result: ValidationResult,
        rule: str,
        value: str | list[object] | None,
        entity_id: str | None = None,
    ) -> None:
        """Validate string/list value is present and non-empty."""
        if isinstance(value, str):
            if value.strip():
                result.add_pass(rule, entity_id)
                return
        elif value:
            result.add_pass(rule, entity_id)
            return
        result.add_fail(rule, entity_id, detail="empty or None")

    @staticmethod
    def check_fk_exists(
        result: ValidationResult,
        rule: str,
        fk_value: str | None,
        existing_ids: set[str],
        entity_id: str | None = None,
    ) -> None:
        """Validate foreign-key target exists."""
        if fk_value is None:
            return
        if fk_value in existing_ids:
            result.add_pass(rule, entity_id)
            return
        result.add_fail(
            rule,
            entity_id,
            detail=f"referenced id '{fk_value}' not found",
        )

    @staticmethod
    def check_true(
        result: ValidationResult,
        rule: str,
        condition: bool,
        entity_id: str | None = None,
        detail: str = "",
    ) -> None:
        """Validate arbitrary boolean condition."""
        if condition:
            result.add_pass(rule, entity_id)
            return
        result.add_fail(rule, entity_id, detail=detail)

    @staticmethod
    def integer_field_names(model: type) -> tuple[str, ...]:
        """Return Integer column field names for model."""
        return tuple(
            column.name
            for column in model.__table__.columns
            if isinstance(column.type, Integer)
        )

    @staticmethod
    def float_field_names(model: type) -> tuple[str, ...]:
        """Return Float/Double column field names for model."""
        return tuple(
            column.name
            for column in model.__table__.columns
            if isinstance(column.type, (Float, Double))
        )

    @staticmethod
    def _competition_scope_clause(selector: str):
        return or_(
            CompetitionEntity.id == selector,
            CompetitionEntity.source_id == selector,
        )

    @staticmethod
    def _season_scope_clause(selector: str):
        return or_(
            SeasonEntity.id == selector,
            SeasonEntity.source_id == selector,
            SeasonEntity.source_id.like(f"%_{selector}"),
        )

    async def _resolve_scoped_season_ids(
        self,
        session: AsyncSession,
        season_id: str | None,
        competition_id: str | None,
    ) -> set[str]:
        """Resolve internal season ids for user-provided selectors."""
        stmt = select(SeasonEntity.id)
        if competition_id:
            stmt = stmt.join(
                CompetitionEntity,
                SeasonEntity.competition_id == CompetitionEntity.id,
            ).where(self._competition_scope_clause(competition_id))
        if season_id:
            stmt = stmt.where(self._season_scope_clause(season_id))
        rows = await session.execute(stmt)
        return {row[0] for row in rows}

    async def _resolve_scoped_competition_ids(
        self,
        session: AsyncSession,
        competition_id: str | None,
        season_id: str | None,
    ) -> set[str]:
        """Resolve internal competition ids for user-provided selectors."""
        stmt = select(CompetitionEntity.id)
        if season_id:
            stmt = stmt.join(
                SeasonEntity,
                SeasonEntity.competition_id == CompetitionEntity.id,
            ).where(self._season_scope_clause(season_id))
        if competition_id:
            stmt = stmt.where(self._competition_scope_clause(competition_id))
        rows = await session.execute(stmt)
        return {row[0] for row in rows}

    @staticmethod
    async def _load_id_set(session: AsyncSession, model: type) -> set[str]:
        """Load primary ids for model."""
        rows = await session.execute(select(model.id))
        return {row[0] for row in rows}
