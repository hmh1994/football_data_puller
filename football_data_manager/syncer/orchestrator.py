import logging
from typing import Callable

try:
    import psutil
except ImportError:  # pragma: no cover - fallback for minimal environments
    psutil = None

from football_data_manager.syncer.container import SyncContainer
from football_data_manager.syncer.dependency import DependencyResolver, SyncEntity
from football_data_manager.syncer.tasks.award import AwardSyncTask
from football_data_manager.syncer.tasks.base import SyncContext, SyncResult
from football_data_manager.syncer.tasks.competition import CompetitionSyncTask
from football_data_manager.syncer.tasks.fixture import FixtureSyncTask
from football_data_manager.syncer.tasks.match import MatchSyncTask
from football_data_manager.syncer.tasks.match_stat import MatchStatSyncTask
from football_data_manager.syncer.tasks.news import NewsSyncTask
from football_data_manager.syncer.tasks.player import PlayerSyncTask
from football_data_manager.syncer.tasks.player_stat import PlayerStatSyncTask
from football_data_manager.syncer.tasks.season import SeasonSyncTask
from football_data_manager.syncer.tasks.team import TeamSyncTask
from football_data_manager.syncer.tasks.team_stat import TeamStatSyncTask

logger = logging.getLogger(__name__)


def _log_memory(step: str) -> float:
    """Log and return current process RSS in MB."""
    if psutil is None:
        logger.info("[Memory] %s: unavailable (psutil missing)", step)
        return 0.0

    rss_mb = psutil.Process().memory_info().rss / 1024 / 1024
    logger.info("[Memory] %s: %.1f MB", step, rss_mb)
    return rss_mb


class SyncOrchestrator:
    """Orchestrate sync tasks in dependency order."""

    def __init__(self, container: SyncContainer):
        self._container = container

    async def sync(
        self,
        target: SyncEntity,
        competition_source_id: str | None = None,
        season_source_id: str | None = None,
        league_abbr: str = "EN_PR",
    ) -> list[SyncResult]:
        execution_order = DependencyResolver.resolve(target)
        return await self._run(
            execution_order=execution_order,
            competition_source_id=competition_source_id,
            season_source_id=season_source_id,
            league_abbr=league_abbr,
        )

    async def sync_all(
        self,
        competition_source_id: str | None = None,
        season_source_id: str | None = None,
        league_abbr: str = "EN_PR",
    ) -> list[SyncResult]:
        execution_order = DependencyResolver.resolve_all()
        return await self._run(
            execution_order=execution_order,
            competition_source_id=competition_source_id,
            season_source_id=season_source_id,
            league_abbr=league_abbr,
        )

    async def _run(
        self,
        execution_order: list[SyncEntity],
        competition_source_id: str | None,
        season_source_id: str | None,
        league_abbr: str,
    ) -> list[SyncResult]:
        context = SyncContext(
            competition_source_id=competition_source_id,
            season_source_id=season_source_id,
            league_abbr=league_abbr,
        )

        results: list[SyncResult] = []
        failed_entities: set[SyncEntity] = set()
        total = len(execution_order)
        entity_names = [e.value for e in execution_order]
        logger.info("Sync started: %s", " -> ".join(entity_names))

        for idx, entity in enumerate(execution_order, 1):
            failed_dep = next(
                (
                    dependency
                    for dependency in failed_entities
                    if DependencyResolver.depends_on(entity, dependency)
                ),
                None,
            )
            if failed_dep is not None:
                logger.warning(
                    "[%d/%d] Skipping %s: dependency '%s' failed",
                    idx, total, entity.value, failed_dep.value,
                )
                results.append(
                    SyncResult(
                        entity=entity.value,
                        skipped=1,
                        messages=[
                            f"Skipped due to failed dependency '{failed_dep.value}'"
                        ],
                    )
                )
                continue

            logger.info("[%d/%d] Syncing %s ...", idx, total, entity.value)
            before_mb = _log_memory(f"Before {entity.value}")
            try:
                task = self._create_task(entity)
                result = await task.execute(context)
            except Exception as error:
                logger.exception("Sync failed for %s", entity.value)
                result = SyncResult(
                    entity=entity.value,
                    errors=1,
                    messages=[str(error)],
                )

            after_mb = _log_memory(f"After {entity.value}")
            result.memory_delta_mb = round(after_mb - before_mb, 2)
            results.append(result)

            logger.info(
                "[%d/%d] Finished %s: created=%d, updated=%d, skipped=%d, errors=%d",
                idx, total, entity.value,
                result.created, result.updated, result.skipped, result.errors,
            )

            if result.errors > 0:
                failed_entities.add(entity)

        total_created = sum(r.created for r in results)
        total_updated = sum(r.updated for r in results)
        total_errors = sum(r.errors for r in results)
        logger.info(
            "Sync finished: created=%d, updated=%d, errors=%d",
            total_created, total_updated, total_errors,
        )
        return results

    def _create_task(
        self,
        entity: SyncEntity,
    ) -> (
        CompetitionSyncTask
        | SeasonSyncTask
        | TeamSyncTask
        | PlayerSyncTask
        | FixtureSyncTask
        | MatchSyncTask
        | MatchStatSyncTask
        | PlayerStatSyncTask
        | TeamStatSyncTask
        | AwardSyncTask
        | NewsSyncTask
    ):
        repositories = self._container.repository_container()
        pullers = self._container.puller_container()
        mergers = self._container.merger_container()
        session_factory = repositories.session_factory()

        builders: dict[SyncEntity, Callable[[], object]] = {
            SyncEntity.COMPETITION: lambda: CompetitionSyncTask(
                session_factory=session_factory,
                puller=pullers.competition_puller(),
                merger=mergers.competition_merger(),
                competition_repo=repositories.competition_repository(),
            ),
            SyncEntity.SEASON: lambda: SeasonSyncTask(
                session_factory=session_factory,
                puller=pullers.season_puller(),
                merger=mergers.season_merger(),
                competition_repo=repositories.competition_repository(),
                season_repo=repositories.season_repository(),
            ),
            SyncEntity.TEAM: lambda: TeamSyncTask(
                session_factory=session_factory,
                puller=pullers.team_puller(),
                merger=mergers.team_merger(),
                competition_repo=repositories.competition_repository(),
                season_repo=repositories.season_repository(),
                team_repo=repositories.team_repository(),
            ),
            SyncEntity.PLAYER: lambda: PlayerSyncTask(
                session_factory=session_factory,
                puller=pullers.player_puller(),
                merger=mergers.player_merger(),
                competition_repo=repositories.competition_repository(),
                season_repo=repositories.season_repository(),
                team_repo=repositories.team_repository(),
                player_repo=repositories.player_repository(),
            ),
            SyncEntity.FIXTURE: lambda: FixtureSyncTask(
                session_factory=session_factory,
                puller=pullers.fixture_puller(),
                merger=mergers.fixture_merger(),
                competition_repo=repositories.competition_repository(),
                season_repo=repositories.season_repository(),
                fixture_repo=repositories.fixture_repository(),
            ),
            SyncEntity.MATCH: lambda: MatchSyncTask(
                session_factory=session_factory,
                merger=mergers.match_merger(),
                competition_repo=repositories.competition_repository(),
                season_repo=repositories.season_repository(),
                fixture_repo=repositories.fixture_repository(),
                match_repo=repositories.match_repository(),
            ),
            SyncEntity.MATCH_STAT: lambda: MatchStatSyncTask(
                session_factory=session_factory,
                puller=pullers.match_stat_puller(),
                merger=mergers.match_stat_merger(),
                match_repo=repositories.match_repository(),
                match_stat_repo=repositories.match_stat_repository(),
            ),
            SyncEntity.PLAYER_STAT: lambda: PlayerStatSyncTask(
                session_factory=session_factory,
                merger=mergers.player_stat_merger(),
                scorer=mergers.player_stat_scorer(),
                competition_repo=repositories.competition_repository(),
                season_repo=repositories.season_repository(),
                player_repo=repositories.player_repository(),
                player_stat_repo=repositories.player_stat_repository(),
            ),
            SyncEntity.TEAM_STAT: lambda: TeamStatSyncTask(
                session_factory=session_factory,
                merger=mergers.team_stat_merger(),
                competition_repo=repositories.competition_repository(),
                season_repo=repositories.season_repository(),
                team_repo=repositories.team_repository(),
                fixture_repo=repositories.fixture_repository(),
                ground_repo=repositories.ground_repository(),
                team_stat_repo=repositories.team_stat_repository(),
            ),
            SyncEntity.AWARD: lambda: AwardSyncTask(
                session_factory=session_factory,
                puller=pullers.award_puller(),
                merger=mergers.award_merger(),
                competition_repo=repositories.competition_repository(),
                season_repo=repositories.season_repository(),
            ),
            SyncEntity.NEWS: lambda: NewsSyncTask(
                session_factory=session_factory,
                merger=mergers.news_merger(),
            ),
        }
        return builders[entity]()

    @staticmethod
    def print_summary(results: list[SyncResult]) -> None:
        """Print concise table-like summary for sync results."""
        headers = ["Entity", "Created", "Updated", "Skipped", "Errors", "Mem(MB)"]
        widths = [15, 8, 8, 8, 7, 8]

        def _line(parts: list[str]) -> str:
            return " | ".join(
                part.ljust(width) for part, width in zip(parts, widths, strict=False)
            )

        total_created = sum(r.created for r in results)
        total_updated = sum(r.updated for r in results)
        total_skipped = sum(r.skipped for r in results)
        total_errors = sum(r.errors for r in results)
        total_mem = sum(r.memory_delta_mb or 0.0 for r in results)

        print(_line(headers))
        print("-" * (sum(widths) + 3 * (len(widths) - 1)))
        for result in results:
            print(
                _line(
                    [
                        result.entity,
                        str(result.created),
                        str(result.updated),
                        str(result.skipped),
                        str(result.errors),
                        f"{result.memory_delta_mb or 0.0:.2f}",
                    ]
                )
            )
        print("-" * (sum(widths) + 3 * (len(widths) - 1)))
        print(
            _line(
                [
                    "Total",
                    str(total_created),
                    str(total_updated),
                    str(total_skipped),
                    str(total_errors),
                    f"{total_mem:.2f}",
                ]
            )
        )
