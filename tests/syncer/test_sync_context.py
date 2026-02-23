import pytest

from football_data_manager.syncer.tasks.base import SyncResult, chunked


def test_sync_result_properties() -> None:
    result = SyncResult(entity="player", created=2, updated=3, skipped=1, errors=0)
    assert result.total == 6
    assert result.success is True

    failed = SyncResult(entity="match", errors=1)
    assert failed.success is False


def test_chunked_batches() -> None:
    assert list(chunked([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]


def test_chunked_rejects_invalid_batch_size() -> None:
    with pytest.raises(ValueError, match="batch_size must be greater than 0"):
        list(chunked([1, 2, 3], 0))
