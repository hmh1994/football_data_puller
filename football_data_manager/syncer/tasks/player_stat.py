import logging

from football_data_manager.merger.mergers.player_stat import PlayerStatMerger
from football_data_manager.merger.scorer import PlayerStatScorer
from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.repositories.competitions import (
    CompetitionRepository,
)
from football_data_manager.repository.repositories.players import PlayerRepository
from football_data_manager.repository.repositories.player_stats import (
    PlayerStatRepository,
)
from football_data_manager.repository.repositories.seasons import SeasonRepository
from football_data_manager.repository.session import SessionFactory
from football_data_manager.syncer.dependency import SyncEntity
from football_data_manager.syncer.tasks.base import (
    AbstractSyncTask,
    SyncContext,
    SyncResult,
    chunked,
    is_updated_within,
)


logger = logging.getLogger(__name__)


class PlayerStatSyncTask(AbstractSyncTask):
    """Sync player-season statistics and compute score fields."""

    BATCH_SIZE = 50

    def __init__(
        self,
        session_factory: SessionFactory,
        merger: PlayerStatMerger,
        scorer: PlayerStatScorer,
        competition_repo: CompetitionRepository,
        season_repo: SeasonRepository,
        player_repo: PlayerRepository,
        player_stat_repo: PlayerStatRepository,
    ):
        super().__init__(session_factory)
        self._merger = merger
        self._scorer = scorer
        self._competition_repo = competition_repo
        self._season_repo = season_repo
        self._player_repo = player_repo
        self._player_stat_repo = player_stat_repo

    async def execute(self, context: SyncContext) -> SyncResult:
        result = SyncResult(entity=SyncEntity.PLAYER_STAT.value)
        if not context.season_source_ids or not context.competition_source_ids:
            logger.warning("Missing competition/season context for player-stat sync")
            result.errors += 1
            result.messages.append(
                "Missing competition/season context for player-stat sync"
            )
            return result
        if not context.player_ids:
            logger.warning("No player_ids in context")
            result.skipped += 1
            result.messages.append("No player_ids in context")
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

        total_players = len(context.player_ids)
        processed = 0

        for player_batch in chunked(context.player_ids, self.BATCH_SIZE):
            logger.info(
                "Processing player stats %d-%d / %d",
                processed + 1, min(processed + len(player_batch), total_players),
                total_players,
            )
            for player_id in player_batch:
                processed += 1
                player = await self._player_repo.get_by_id(player_id)
                if player is None:
                    result.errors += 1
                    result.messages.append(f"Player id '{player_id}' not found")
                    continue

                source_id = PlayerStatEntity.get_source_id(season, player)
                existing = await self._player_stat_repo.get_by_pulselive_id(source_id)
                if existing and is_updated_within(existing):
                    result.skipped += 1
                    continue

                try:
                    merged = await self._merger.merge(player, competition, season)
                except Exception as error:
                    logger.exception(
                        "Player-stat sync failed for player_id=%s player_source_id=%s",
                        player.id,
                        player.source_id,
                    )
                    result.errors += 1
                    result.messages.append(
                        "Player-stat sync failed for "
                        f"player_id='{player.id}' player_source_id='{player.source_id}': "
                        f"{error}"
                    )
                    continue
                if merged is None:
                    result.skipped += 1
                    continue

                scored = self._scorer.score(merged, player.position)
                await self._player_stat_repo.update(scored)

                if existing is None:
                    result.created += 1
                else:
                    result.updated += 1

        return result
