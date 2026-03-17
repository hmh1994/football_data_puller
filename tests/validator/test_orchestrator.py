from types import SimpleNamespace

import pytest

from football_data_manager.validator.orchestrator import (
    VALIDATE_ORDER,
    ValidateEntity,
    ValidationOrchestrator,
)
from football_data_manager.validator.validators.base import ValidationResult


class _FakeValidator:
    def __init__(self, entity: str, trace: list[str], fail: bool = False):
        self._entity = entity
        self._trace = trace
        self._fail = fail

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        _ = season_id, competition_id
        self._trace.append(self._entity)
        if self._fail:
            raise RuntimeError("boom")
        result = ValidationResult(entity=self._entity)
        result.add_pass("ok")
        return result


@pytest.mark.asyncio
async def test_orchestrator_validate_single_target() -> None:
    trace: list[str] = []
    container = SimpleNamespace(
        create_validator=lambda entity: _FakeValidator(entity=entity, trace=trace)
    )
    orchestrator = ValidationOrchestrator(container=container)

    results = await orchestrator.validate(
        target=ValidateEntity.MATCH,
        season_id="578",
        competition_id="8",
    )

    assert trace == ["match"]
    assert [result.entity for result in results] == ["match"]
    assert results[0].success is True


@pytest.mark.asyncio
async def test_orchestrator_validate_all_order_and_failure_capture() -> None:
    trace: list[str] = []

    def _factory(entity: str):
        return _FakeValidator(
            entity=entity,
            trace=trace,
            fail=(entity == ValidateEntity.MATCH_STAT.value),
        )

    orchestrator = ValidationOrchestrator(
        container=SimpleNamespace(create_validator=_factory)
    )

    results = await orchestrator.validate_all()

    assert trace == [entity.value for entity in VALIDATE_ORDER]
    assert [result.entity for result in results] == [
        entity.value for entity in VALIDATE_ORDER
    ]
    by_entity = {result.entity: result for result in results}
    assert by_entity["match-stat"].success is False
    assert by_entity["match-stat"].fail_count == 1

