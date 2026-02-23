from types import SimpleNamespace

import pytest

from football_data_manager.syncer.dependency import SyncEntity
from football_data_manager.syncer.orchestrator import SyncOrchestrator
from football_data_manager.syncer.tasks.base import SyncContext, SyncResult


class _FakeTask:
    def __init__(
        self,
        entity: SyncEntity,
        trace: list[str],
        fail: bool = False,
    ):
        self._entity = entity
        self._trace = trace
        self._fail = fail

    async def execute(self, context: SyncContext) -> SyncResult:
        _ = context
        self._trace.append(self._entity.value)
        if self._fail:
            return SyncResult(entity=self._entity.value, errors=1, messages=["boom"])
        return SyncResult(entity=self._entity.value, updated=1)


@pytest.mark.asyncio
async def test_orchestrator_runs_resolved_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trace: list[str] = []
    orchestrator = SyncOrchestrator(container=SimpleNamespace())

    tasks = {entity: _FakeTask(entity=entity, trace=trace) for entity in SyncEntity}
    monkeypatch.setattr(orchestrator, "_create_task", lambda entity: tasks[entity])

    results = await orchestrator.sync(
        target=SyncEntity.TEAM_STAT,
        competition_source_id="1",
        season_source_id="578",
    )

    expected = [
        "competition",
        "season",
        "team",
        "player",
        "fixture",
        "match",
        "team-stat",
    ]
    assert trace == expected
    assert [result.entity for result in results] == expected
    assert all(result.errors == 0 for result in results)
    assert all(result.memory_delta_mb is not None for result in results)


@pytest.mark.asyncio
async def test_orchestrator_skips_dependents_but_runs_independent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trace: list[str] = []
    orchestrator = SyncOrchestrator(container=SimpleNamespace())

    tasks = {
        entity: _FakeTask(
            entity=entity,
            trace=trace,
            fail=(entity == SyncEntity.COMPETITION),
        )
        for entity in SyncEntity
    }
    monkeypatch.setattr(orchestrator, "_create_task", lambda entity: tasks[entity])

    results = await orchestrator.sync_all(
        competition_source_id="1",
        season_source_id="578",
    )

    by_entity = {result.entity: result for result in results}

    assert trace == ["competition", "news"]
    assert by_entity["competition"].errors == 1
    assert by_entity["season"].skipped == 1
    assert by_entity["team"].skipped == 1
    assert by_entity["award"].skipped == 1
    assert by_entity["news"].updated == 1
