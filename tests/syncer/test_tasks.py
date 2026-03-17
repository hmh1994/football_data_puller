from types import SimpleNamespace

import pytest

from football_data_manager.syncer.tasks.base import SyncContext
from football_data_manager.syncer.tasks.match import MatchSyncTask
from football_data_manager.syncer.tasks.player_stat import PlayerStatSyncTask


@pytest.mark.asyncio
async def test_match_sync_task_continues_after_fixture_failure() -> None:
    fixture_1 = SimpleNamespace(id="fixture-1", source_id="m-1")
    fixture_2 = SimpleNamespace(id="fixture-2", source_id="m-2")

    class _CompetitionRepo:
        async def get_by_pulselive_id(self, source_id: str):
            _ = source_id
            return SimpleNamespace(id="competition-1")

    class _SeasonRepo:
        async def get_by_pulselive_id(self, source_id: str):
            _ = source_id
            return SimpleNamespace(id="season-1")

    class _FixtureRepo:
        async def get_by_id(self, fixture_id: str):
            return {
                "fixture-1": fixture_1,
                "fixture-2": fixture_2,
            }.get(fixture_id)

    class _MatchRepo:
        async def get_by_pulselive_id(self, source_id: str):
            _ = source_id
            return None

    class _Merger:
        async def merge_from_api(self, fixture, competition, season):
            _ = competition, season
            if fixture.source_id == "m-1":
                raise RuntimeError("boom")
            return SimpleNamespace(id="match-2")

    task = MatchSyncTask(
        session_factory=SimpleNamespace(),
        merger=_Merger(),
        competition_repo=_CompetitionRepo(),
        season_repo=_SeasonRepo(),
        fixture_repo=_FixtureRepo(),
        match_repo=_MatchRepo(),
    )
    context = SyncContext(
        competition_source_ids=["1"],
        season_source_ids=["2024"],
        fixture_ids=["fixture-1", "fixture-2"],
    )

    result = await task.execute(context)

    assert result.errors == 1
    assert result.created == 1
    assert context.match_ids == ["match-2"]
    assert "fixture_id='fixture-1'" in result.messages[0]
    assert "match_source_id='m-1'" in result.messages[0]


@pytest.mark.asyncio
async def test_player_stat_sync_task_continues_after_player_failure() -> None:
    player_1 = SimpleNamespace(id="player-1", source_id="100")
    player_2 = SimpleNamespace(id="player-2", source_id="200", position=None)

    class _CompetitionRepo:
        async def get_by_pulselive_id(self, source_id: str):
            _ = source_id
            return SimpleNamespace(id="competition-1")

    class _SeasonRepo:
        async def get_by_pulselive_id(self, source_id: str):
            _ = source_id
            return SimpleNamespace(id="season-1", source_id="8_2024")

    class _PlayerRepo:
        async def get_by_id(self, player_id: str):
            return {
                "player-1": player_1,
                "player-2": player_2,
            }.get(player_id)

    class _PlayerStatRepo:
        async def get_by_pulselive_id(self, source_id: str):
            _ = source_id
            return None

        async def update(self, entity):
            return entity

    class _Merger:
        async def merge(self, player, competition, season):
            _ = competition, season
            if player.source_id == "100":
                raise RuntimeError("boom")
            return SimpleNamespace(id="player-stat-2")

    class _Scorer:
        def score(self, merged, position):
            _ = position
            return merged

    task = PlayerStatSyncTask(
        session_factory=SimpleNamespace(),
        merger=_Merger(),
        scorer=_Scorer(),
        competition_repo=_CompetitionRepo(),
        season_repo=_SeasonRepo(),
        player_repo=_PlayerRepo(),
        player_stat_repo=_PlayerStatRepo(),
    )
    context = SyncContext(
        competition_source_ids=["8"],
        season_source_ids=["8_2024"],
        player_ids=["player-1", "player-2"],
    )

    result = await task.execute(context)

    assert result.errors == 1
    assert result.created == 1
    assert "player_id='player-1'" in result.messages[0]
    assert "player_source_id='100'" in result.messages[0]
