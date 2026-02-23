import logging

from football_data_manager.merger.mergers.award import AwardMerger
from football_data_manager.puller.pullers.pulselive.award import AwardPuller
from football_data_manager.repository.repositories.competitions import (
    CompetitionRepository,
)
from football_data_manager.repository.repositories.seasons import SeasonRepository
from football_data_manager.repository.session import SessionFactory
from football_data_manager.syncer.dependency import SyncEntity
from football_data_manager.syncer.tasks.base import (
    AbstractSyncTask,
    SyncContext,
    SyncResult,
)


logger = logging.getLogger(__name__)


class AwardSyncTask(AbstractSyncTask):
    """Sync season awards and related associations."""

    def __init__(
        self,
        session_factory: SessionFactory,
        puller: AwardPuller,
        merger: AwardMerger,
        competition_repo: CompetitionRepository,
        season_repo: SeasonRepository,
    ):
        super().__init__(session_factory)
        self._puller = puller
        self._merger = merger
        self._competition_repo = competition_repo
        self._season_repo = season_repo

    async def execute(self, context: SyncContext) -> SyncResult:
        result = SyncResult(entity=SyncEntity.AWARD.value)
        if not context.season_source_ids:
            logger.warning("No season_source_ids in context")
            result.skipped += 1
            result.messages.append("No season_source_ids in context")
            return result

        total_seasons = len(context.season_source_ids)
        for idx, season_source_id in enumerate(context.season_source_ids, 1):
            logger.info(
                "Pulling awards for season %s (%d/%d)",
                season_source_id, idx, total_seasons,
            )
            season = await self._season_repo.get_by_pulselive_id(season_source_id)
            if season is None:
                logger.warning("Season '%s' not found in DB", season_source_id)
                result.errors += 1
                result.messages.append(f"Season '{season_source_id}' not found in DB")
                continue

            competition = await self._competition_repo.get_by_id(season.competition_id)
            if competition is None:
                result.errors += 1
                result.messages.append(
                    f"Competition id '{season.competition_id}' not found for season"
                )
                continue

            response = await self._puller.pull_awards(
                competition.source_id,
                season.source_id.split("_")[-1],
            )
            awards, player_stats, staffs = await self._merger.merge(
                competition, season, response
            )
            logger.info(
                "Merged %d awards, %d player_stats, %d staffs",
                len(awards), len(player_stats), len(staffs),
            )
            result.updated += len(awards) + len(player_stats) + len(staffs)

        return result
