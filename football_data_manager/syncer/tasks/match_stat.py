import logging

from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.merger.mergers.match_stat import MatchStatMerger
from football_data_manager.puller.pullers.pulselive.match_stat import MatchStatPuller
from football_data_manager.repository.repositories.match_stats import (
    MatchStatRepository,
)
from football_data_manager.repository.repositories.matches import MatchRepository
from football_data_manager.repository.session import SessionFactory
from football_data_manager.syncer.dependency import SyncEntity
from football_data_manager.syncer.tasks.base import (
    AbstractSyncTask,
    SyncContext,
    SyncResult,
    chunked,
)


logger = logging.getLogger(__name__)


class MatchStatSyncTask(AbstractSyncTask):
    """Sync match statistics in batches from match IDs."""

    BATCH_SIZE = 50

    def __init__(
        self,
        session_factory: SessionFactory,
        puller: MatchStatPuller,
        merger: MatchStatMerger,
        match_repo: MatchRepository,
        match_stat_repo: MatchStatRepository,
    ):
        super().__init__(session_factory)
        self._puller = puller
        self._merger = merger
        self._match_repo = match_repo
        self._match_stat_repo = match_stat_repo

    async def execute(self, context: SyncContext) -> SyncResult:
        result = SyncResult(entity=SyncEntity.MATCH_STAT.value)
        if not context.match_ids:
            logger.warning("No match_ids in context")
            result.skipped += 1
            result.messages.append("No match_ids in context")
            return result

        total_matches = len(context.match_ids)
        processed = 0

        for match_batch in chunked(context.match_ids, self.BATCH_SIZE):
            logger.info(
                "Processing match stats %d-%d / %d",
                processed + 1, min(processed + len(match_batch), total_matches),
                total_matches,
            )
            for match_id in match_batch:
                processed += 1
                match = await self._match_repo.get_by_id(match_id)
                if match is None:
                    result.errors += 1
                    result.messages.append(f"Match id '{match_id}' not found")
                    continue
                if match.period != PeriodEnum.FULLTIME:
                    result.skipped += 1
                    continue

                response = await self._puller.pull_match_stat(match.source_id)
                existing_source_ids = {
                    f"{match.source_id}_{str(item.team_id)}"
                    for item in response
                    if await self._match_stat_repo.get_by_pulselive_id(
                        f"{match.source_id}_{str(item.team_id)}"
                    )
                    is not None
                }

                merged = await self._merger.merge(match, response)
                for item in merged:
                    if item.source_id in existing_source_ids:
                        result.updated += 1
                    else:
                        result.created += 1

        return result
