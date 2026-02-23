import logging

from football_data_manager.merger.mergers.news import NewsMerger
from football_data_manager.repository.session import SessionFactory
from football_data_manager.syncer.dependency import SyncEntity
from football_data_manager.syncer.tasks.base import (
    AbstractSyncTask,
    SyncContext,
    SyncResult,
)


logger = logging.getLogger(__name__)


class NewsSyncTask(AbstractSyncTask):
    """Sync league news from The Athletic."""

    def __init__(
        self,
        session_factory: SessionFactory,
        merger: NewsMerger,
    ):
        super().__init__(session_factory)
        self._merger = merger

    async def execute(self, context: SyncContext) -> SyncResult:
        result = SyncResult(entity=SyncEntity.NEWS.value)
        logger.info("Pulling news feed for league '%s'", context.league_abbr)
        created_news = await self._merger.merge_league_feed(
            league_abbr=context.league_abbr
        )
        result.created += len(created_news)
        logger.info("Created %d news articles", len(created_news))
        await self._merger.close()
        return result
