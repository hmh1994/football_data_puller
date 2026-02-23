import logging

from football_data_manager.merger.mergers.season import SeasonMerger
from football_data_manager.puller.interfaces.pulselive.v1_competition import (
    V1CompetitionDetailResponse,
)
from football_data_manager.puller.pullers.pulselive.season import SeasonPuller
from football_data_manager.repository.entities.seasons import SeasonEntity
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
    append_unique,
    is_updated_within,
)


logger = logging.getLogger(__name__)


class SeasonSyncTask(AbstractSyncTask):
    """Sync seasons for selected competitions."""

    def __init__(
        self,
        session_factory: SessionFactory,
        puller: SeasonPuller,
        merger: SeasonMerger,
        competition_repo: CompetitionRepository,
        season_repo: SeasonRepository,
    ):
        super().__init__(session_factory)
        self._puller = puller
        self._merger = merger
        self._competition_repo = competition_repo
        self._season_repo = season_repo

    async def execute(self, context: SyncContext) -> SyncResult:
        result = SyncResult(entity=SyncEntity.SEASON.value)
        if not context.competition_source_ids:
            logger.warning("No competition_source_ids in context")
            result.errors += 1
            result.messages.append("No competition_source_ids in context")
            return result

        total_comps = len(context.competition_source_ids)
        for comp_idx, competition_source_id in enumerate(
            context.competition_source_ids, 1
        ):
            logger.info(
                "Pulling seasons for competition %s (%d/%d)",
                competition_source_id, comp_idx, total_comps,
            )
            competition = await self._competition_repo.get_by_pulselive_id(
                competition_source_id
            )
            if competition is None:
                logger.warning(
                    "Competition '%s' not found in DB", competition_source_id,
                )
                result.errors += 1
                result.messages.append(
                    f"Competition '{competition_source_id}' not found in DB"
                )
                continue

            if context.season_source_id:
                merged_sid = SeasonEntity.get_source_id(
                    competition, context.season_source_id
                )
                existing_season = await self._season_repo.get_by_pulselive_id(merged_sid)
                if existing_season and is_updated_within(existing_season):
                    logger.info(
                        "Season '%s' is fresh, skipping pull", merged_sid,
                    )
                    append_unique(context.season_ids, existing_season.id)
                    append_unique(context.season_source_ids, existing_season.source_id)
                    result.skipped += 1
                    continue

            response = await self._puller.pull_seasons(competition_source_id)
            seasons = response.seasons
            if context.season_source_id:
                seasons = [
                    season
                    for season in seasons
                    if str(season["id"]) == str(context.season_source_id)
                ]

            if not seasons:
                logger.debug("No matching seasons found for competition %s", competition_source_id)
                continue

            logger.info("Merging %d seasons for competition %s", len(seasons), competition_source_id)
            known_source_ids = {
                SeasonEntity.get_source_id(competition, str(season["id"]))
                for season in seasons
                if await self._season_repo.get_by_pulselive_id(
                    SeasonEntity.get_source_id(competition, str(season["id"]))
                )
                is not None
            }
            filtered: V1CompetitionDetailResponse = response.model_copy(
                update={"seasons": seasons}
            )
            merged = await self._merger.merge(competition, filtered)
            for season in merged:
                if season.source_id in known_source_ids:
                    result.updated += 1
                else:
                    result.created += 1
                append_unique(context.season_ids, season.id)
                append_unique(context.season_source_ids, season.source_id)

        if context.season_source_id and not context.season_source_ids:
            logger.warning("Season '%s' not found", context.season_source_id)
            result.messages.append(f"Season '{context.season_source_id}' not found")
            result.skipped += 1

        return result
