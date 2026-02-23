import logging

from football_data_manager.merger.mergers.competition import CompetitionMerger
from football_data_manager.puller.interfaces.pulselive.v1_competition import (
    V1CompetitionResponse,
)
from football_data_manager.puller.pullers.pulselive.competition import CompetitionPuller
from football_data_manager.repository.repositories.competitions import (
    CompetitionRepository,
)
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


class CompetitionSyncTask(AbstractSyncTask):
    """Sync competition data from Pulselive into DB."""

    def __init__(
        self,
        session_factory: SessionFactory,
        puller: CompetitionPuller,
        merger: CompetitionMerger,
        competition_repo: CompetitionRepository,
    ):
        super().__init__(session_factory)
        self._puller = puller
        self._merger = merger
        self._competition_repo = competition_repo

    async def execute(self, context: SyncContext) -> SyncResult:
        result = SyncResult(entity=SyncEntity.COMPETITION.value)

        if context.competition_source_id:
            existing = await self._competition_repo.get_by_pulselive_id(
                context.competition_source_id
            )
            if existing and is_updated_within(existing):
                logger.info(
                    "Competition '%s' is fresh, skipping pull",
                    context.competition_source_id,
                )
                append_unique(context.competition_ids, existing.id)
                append_unique(context.competition_source_ids, existing.source_id)
                result.skipped += 1
                return result

        cursor: str | None = None
        page = 0

        while True:
            page += 1
            logger.debug("Pulling competitions page %d (cursor=%s)", page, cursor)
            response = await self._puller.pull_competitions(limit=50, _next=cursor)
            selected = response.data
            if context.competition_source_id:
                selected = [
                    item
                    for item in selected
                    if str(item["id"]) == str(context.competition_source_id)
                ]

            if selected:
                logger.info("Merging %d competitions (page %d)", len(selected), page)
                filtered: V1CompetitionResponse = response.model_copy(
                    update={"data": selected}
                )
                known_source_ids = {
                    str(item["id"])
                    for item in selected
                    if await self._competition_repo.get_by_pulselive_id(str(item["id"]))
                    is not None
                }
                merged = await self._merger.merge(filtered)
                for entity in merged:
                    if entity.source_id in known_source_ids:
                        result.updated += 1
                    else:
                        result.created += 1
                    append_unique(context.competition_ids, entity.id)
                    append_unique(context.competition_source_ids, entity.source_id)

            cursor = response.pagination.get("_next")
            if cursor is None:
                break

        if context.competition_source_id and not context.competition_source_ids:
            logger.warning(
                "Competition '%s' not found", context.competition_source_id,
            )
            result.messages.append(
                f"Competition '{context.competition_source_id}' not found"
            )
            result.skipped += 1

        return result
