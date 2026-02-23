import logging

from football_data_manager.merger.mergers.player import PlayerMerger
from football_data_manager.puller.pullers.pulselive.player import PlayerPuller
from football_data_manager.repository.repositories.competitions import (
    CompetitionRepository,
)
from football_data_manager.repository.repositories.players import PlayerRepository
from football_data_manager.repository.repositories.seasons import SeasonRepository
from football_data_manager.repository.repositories.teams import TeamRepository
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


class PlayerSyncTask(AbstractSyncTask):
    """Sync player squads in team batches."""

    BATCH_SIZE = 5

    def __init__(
        self,
        session_factory: SessionFactory,
        puller: PlayerPuller,
        merger: PlayerMerger,
        competition_repo: CompetitionRepository,
        season_repo: SeasonRepository,
        team_repo: TeamRepository,
        player_repo: PlayerRepository,
    ):
        super().__init__(session_factory)
        self._puller = puller
        self._merger = merger
        self._competition_repo = competition_repo
        self._season_repo = season_repo
        self._team_repo = team_repo
        self._player_repo = player_repo

    async def execute(self, context: SyncContext) -> SyncResult:
        result = SyncResult(entity=SyncEntity.PLAYER.value)
        if not context.season_source_ids or not context.competition_source_ids:
            logger.warning("Missing competition/season context for player sync")
            result.errors += 1
            result.messages.append("Missing competition/season context for player sync")
            return result
        if not context.team_source_ids:
            logger.warning("No team_source_ids in context")
            result.errors += 1
            result.messages.append("No team_source_ids in context")
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
        total_teams = len(context.team_source_ids)
        processed = 0

        for team_batch in chunked(context.team_source_ids, self.BATCH_SIZE):
            for team_source_id in team_batch:
                processed += 1
                team = await self._team_repo.get_by_pulselive_id(team_source_id)
                if team is None:
                    logger.warning("Team '%s' not found in DB", team_source_id)
                    result.errors += 1
                    result.messages.append(f"Team '{team_source_id}' not found in DB")
                    continue

                logger.info(
                    "Pulling squad for team %s (%d/%d)",
                    team.name_en or team_source_id, processed, total_teams,
                )
                response = await self._puller.pull_squad(
                    competition.source_id,
                    raw_season_source_id,
                    team_source_id,
                )
                known_source_ids = {
                    player.id["player_id"]
                    for player in response.players
                    if await self._player_repo.get_by_pulselive_id(
                        player.id["player_id"]
                    )
                    is not None
                }

                merged = await self._merger.merge(competition, season, team, response)
                logger.debug(
                    "Merged %d players for team %s",
                    len(merged), team_source_id,
                )
                for player in merged:
                    if player.source_id in known_source_ids:
                        result.updated += 1
                    else:
                        result.created += 1
                    append_unique(context.player_ids, player.id)
                    append_unique(context.player_source_ids, player.source_id)

        return result
