import logging

from football_data_manager.merger.mergers.fixture import FixtureMerger
from football_data_manager.puller.interfaces.pulselive.v1_match import (
    V1MatchweekMatchesResponse,
)
from football_data_manager.puller.pullers.pulselive.fixture import FixturePuller
from football_data_manager.repository.repositories.competitions import (
    CompetitionRepository,
)
from football_data_manager.repository.repositories.fixtures import FixtureRepository
from football_data_manager.repository.repositories.seasons import SeasonRepository
from football_data_manager.repository.session import SessionFactory
from football_data_manager.syncer.dependency import SyncEntity
from football_data_manager.syncer.tasks.base import (
    AbstractSyncTask,
    SyncContext,
    SyncResult,
    append_unique,
    chunked,
)


logger = logging.getLogger(__name__)


class FixtureSyncTask(AbstractSyncTask):
    """Sync season fixtures in matchweek batches."""

    BATCH_SIZE = 5
    MATCHWEEKS = range(1, 39)

    def __init__(
        self,
        session_factory: SessionFactory,
        puller: FixturePuller,
        merger: FixtureMerger,
        competition_repo: CompetitionRepository,
        season_repo: SeasonRepository,
        fixture_repo: FixtureRepository,
    ):
        super().__init__(session_factory)
        self._puller = puller
        self._merger = merger
        self._competition_repo = competition_repo
        self._season_repo = season_repo
        self._fixture_repo = fixture_repo

    async def execute(self, context: SyncContext) -> SyncResult:
        result = SyncResult(entity=SyncEntity.FIXTURE.value)
        if not context.season_source_ids or not context.competition_source_ids:
            logger.warning("Missing competition/season context for fixture sync")
            result.errors += 1
            result.messages.append(
                "Missing competition/season context for fixture sync"
            )
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

        raw_season_source_id = season.source_id.split("_")[-1]
        total_mw = len(self.MATCHWEEKS)

        for matchweek_batch in chunked(self.MATCHWEEKS, self.BATCH_SIZE):
            first_mw = matchweek_batch[0]
            last_mw = matchweek_batch[-1]
            logger.info(
                "Processing matchweeks %d-%d / %d", first_mw, last_mw, total_mw,
            )
            for matchweek in matchweek_batch:
                cursor: str | None = None
                while True:
                    response = await self._puller.pull_matchweek_matches(
                        competition.source_id,
                        raw_season_source_id,
                        matchweek,
                        limit=50,
                        _next=cursor,
                    )
                    if response.data:
                        known_source_ids = {
                            str(match["match_id"])
                            for match in response.data
                            if await self._fixture_repo.get_by_pulselive_id(
                                str(match["match_id"])
                            )
                            is not None
                        }
                        filtered: V1MatchweekMatchesResponse = response.model_copy(
                            update={"data": response.data}
                        )
                        fixtures = await self._merger.merge(season, matchweek, filtered)
                        logger.debug(
                            "MW %d: merged %d fixtures", matchweek, len(fixtures),
                        )
                        for fixture in fixtures:
                            if fixture.source_id in known_source_ids:
                                result.updated += 1
                            else:
                                result.created += 1
                            append_unique(context.fixture_ids, fixture.id)

                    cursor = response.pagination.get("_next")
                    if cursor is None:
                        break

        return result
