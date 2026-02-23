import pytest

from football_data_manager.syncer.dependency import (
    DEPENDENCY_GRAPH,
    DependencyResolver,
    SyncEntity,
)


def test_dependency_resolve_expected_orders() -> None:
    assert DependencyResolver.resolve(SyncEntity.COMPETITION) == [
        SyncEntity.COMPETITION
    ]
    assert DependencyResolver.resolve(SyncEntity.SEASON) == [
        SyncEntity.COMPETITION,
        SyncEntity.SEASON,
    ]
    assert DependencyResolver.resolve(SyncEntity.TEAM) == [
        SyncEntity.COMPETITION,
        SyncEntity.SEASON,
        SyncEntity.TEAM,
    ]
    assert DependencyResolver.resolve(SyncEntity.PLAYER) == [
        SyncEntity.COMPETITION,
        SyncEntity.SEASON,
        SyncEntity.TEAM,
        SyncEntity.PLAYER,
    ]
    assert DependencyResolver.resolve(SyncEntity.MATCH_STAT) == [
        SyncEntity.COMPETITION,
        SyncEntity.SEASON,
        SyncEntity.TEAM,
        SyncEntity.PLAYER,
        SyncEntity.FIXTURE,
        SyncEntity.MATCH,
        SyncEntity.MATCH_STAT,
    ]
    assert DependencyResolver.resolve(SyncEntity.PLAYER_STAT) == [
        SyncEntity.COMPETITION,
        SyncEntity.SEASON,
        SyncEntity.TEAM,
        SyncEntity.PLAYER,
        SyncEntity.PLAYER_STAT,
    ]
    assert DependencyResolver.resolve(SyncEntity.TEAM_STAT) == [
        SyncEntity.COMPETITION,
        SyncEntity.SEASON,
        SyncEntity.TEAM,
        SyncEntity.PLAYER,
        SyncEntity.FIXTURE,
        SyncEntity.MATCH,
        SyncEntity.TEAM_STAT,
    ]
    assert DependencyResolver.resolve(SyncEntity.AWARD) == [
        SyncEntity.COMPETITION,
        SyncEntity.SEASON,
        SyncEntity.TEAM,
        SyncEntity.PLAYER,
        SyncEntity.FIXTURE,
        SyncEntity.MATCH,
        SyncEntity.PLAYER_STAT,
        SyncEntity.AWARD,
    ]
    assert DependencyResolver.resolve(SyncEntity.NEWS) == [SyncEntity.NEWS]


def test_dependency_resolve_all_order() -> None:
    assert DependencyResolver.resolve_all() == [
        SyncEntity.COMPETITION,
        SyncEntity.SEASON,
        SyncEntity.TEAM,
        SyncEntity.PLAYER,
        SyncEntity.FIXTURE,
        SyncEntity.MATCH,
        SyncEntity.MATCH_STAT,
        SyncEntity.PLAYER_STAT,
        SyncEntity.TEAM_STAT,
        SyncEntity.AWARD,
        SyncEntity.NEWS,
    ]


def test_dependency_cycle_detection(monkeypatch: pytest.MonkeyPatch) -> None:
    looped_graph = dict(DEPENDENCY_GRAPH)
    looped_graph[SyncEntity.COMPETITION] = [SyncEntity.AWARD]
    monkeypatch.setattr(
        "football_data_manager.syncer.dependency.DEPENDENCY_GRAPH",
        looped_graph,
    )

    with pytest.raises(ValueError, match="Dependency cycle detected"):
        DependencyResolver.resolve(SyncEntity.AWARD)
