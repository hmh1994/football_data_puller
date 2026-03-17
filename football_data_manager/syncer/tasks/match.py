import logging

from football_data_manager.merger.mergers.match import MatchMerger
from football_data_manager.repository.repositories.competitions import (
    CompetitionRepository,
)
from football_data_manager.repository.repositories.fixtures import FixtureRepository
from football_data_manager.repository.repositories.matches import MatchRepository
from football_data_manager.repository.repositories.seasons import SeasonRepository
from football_data_manager.repository.session import SessionFactory
from football_data_manager.syncer.dependency import SyncEntity
from football_data_manager.syncer.tasks.base import (
    AbstractSyncTask,
    SyncContext,
    SyncResult,
    append_unique,
    chunked,
    is_updated_within,
)


logger = logging.getLogger(__name__)


class MatchSyncTask(AbstractSyncTask):
    """Sync matches from fixture IDs in batched API requests."""

    BATCH_SIZE = 25

    def __init__(
        self,
        session_factory: SessionFactory,
        merger: MatchMerger,
        competition_repo: CompetitionRepository,
        season_repo: SeasonRepository,
        fixture_repo: FixtureRepository,
        match_repo: MatchRepository,
    ):
        super().__init__(session_factory)
        self._merger = merger
        self._competition_repo = competition_repo
        self._season_repo = season_repo
        self._fixture_repo = fixture_repo
        self._match_repo = match_repo

    async def execute(self, context: SyncContext) -> SyncResult:
        result = SyncResult(entity=SyncEntity.MATCH.value)
        if not context.season_source_ids or not context.competition_source_ids:
            logger.warning("Missing competition/season context for match sync")
            result.errors += 1
            result.messages.append("Missing competition/season context for match sync")
            return result
        if not context.fixture_ids:
            logger.warning("No fixture_ids in context")
            result.skipped += 1
            result.messages.append("No fixture_ids in context")
            return result

        competition = await self._competition_repo.get_by_pulselive_id(
            context.competition_source_ids[0]
        )
        season = await self._season_repo.get_by_pulselive_id(
            context.season_source_ids[0]
        )
        if competition is None or season is None:
            result.errors += 1
            result.messages.append("Competition or season not found in DB")
            return result

        total_fixtures = len(context.fixture_ids)
        processed = 0

        for fixture_batch in chunked(context.fixture_ids, self.BATCH_SIZE):
            logger.info(
                "Processing fixtures %d-%d / %d",
                processed + 1, min(processed + len(fixture_batch), total_fixtures),
                total_fixtures,
            )
            for fixture_id in fixture_batch:
                processed += 1
                fixture = await self._fixture_repo.get_by_id(fixture_id)
                if fixture is None:
                    result.errors += 1
                    result.messages.append(f"Fixture id '{fixture_id}' not found")
                    continue

                existing = await self._match_repo.get_by_pulselive_id(fixture.source_id)
                if existing and is_updated_within(existing):
                    append_unique(context.match_ids, existing.id)
                    result.skipped += 1
                    continue

                try:
                    merged = await self._merger.merge_from_api(
                        fixture,
                        competition,
                        season,
                    )
                except Exception as error:
                    logger.exception(
                        "Match sync failed for fixture_id=%s match_source_id=%s",
                        fixture.id,
                        fixture.source_id,
                    )
                    result.errors += 1
                    result.messages.append(
                        "Match sync failed for "
                        f"fixture_id='{fixture.id}' match_source_id='{fixture.source_id}': "
                        f"{error}"
                    )
                    continue
                if merged is None:
                    result.skipped += 1
                    continue

                if existing is None:
                    result.created += 1
                else:
                    result.updated += 1
                append_unique(context.match_ids, merged.id)

        return result
