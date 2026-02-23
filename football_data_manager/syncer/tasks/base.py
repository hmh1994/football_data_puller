from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, Iterator, TypeVar

from football_data_manager.merger.utils import is_updated_within
from football_data_manager.repository.session import SessionFactory

T = TypeVar("T")


@dataclass
class SyncResult:
    """Result for one sync task execution."""

    entity: str
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: int = 0
    messages: list[str] = field(default_factory=list)
    memory_delta_mb: float | None = None

    @property
    def total(self) -> int:
        return self.created + self.updated + self.skipped

    @property
    def success(self) -> bool:
        return self.errors == 0


@dataclass
class SyncContext:
    """Lightweight context shared across sync tasks."""

    competition_source_id: str | None = None
    season_source_id: str | None = None
    league_abbr: str = "EN_PR"

    competition_ids: list[str] = field(default_factory=list)
    season_ids: list[str] = field(default_factory=list)
    team_ids: list[str] = field(default_factory=list)
    player_ids: list[str] = field(default_factory=list)
    fixture_ids: list[str] = field(default_factory=list)
    match_ids: list[str] = field(default_factory=list)
    ground_ids: list[str] = field(default_factory=list)

    competition_source_ids: list[str] = field(default_factory=list)
    season_source_ids: list[str] = field(default_factory=list)
    team_source_ids: list[str] = field(default_factory=list)
    player_source_ids: list[str] = field(default_factory=list)


def chunked(items: Iterable[T], batch_size: int) -> Iterator[list[T]]:
    """Yield fixed-size batches from an iterable."""
    if batch_size <= 0:
        raise ValueError("batch_size must be greater than 0")

    batch: list[T] = []
    for item in items:
        batch.append(item)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


def append_unique(target: list[str], value: str | None) -> None:
    """Append to list only when value is non-empty and absent."""
    if value and value not in target:
        target.append(value)


def extend_unique(target: list[str], values: Iterable[str]) -> None:
    """Append many values with list-order preservation and deduplication."""
    for value in values:
        append_unique(target, value)


class AbstractSyncTask(ABC):
    """Base class for all sync tasks."""

    def __init__(self, session_factory: SessionFactory):
        self._session_factory = session_factory

    @abstractmethod
    async def execute(self, context: SyncContext) -> SyncResult:
        """Execute sync task and mutate context with downstream IDs."""
        raise NotImplementedError
