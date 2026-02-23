import logging

from football_data_manager.merger.mergers.team import TeamMerger
from football_data_manager.puller.interfaces.pulselive.v1_team import V1TeamsResponse
from football_data_manager.puller.pullers.pulselive.team import TeamPuller
from football_data_manager.repository.repositories.competitions import (
    CompetitionRepository,
)
from football_data_manager.repository.repositories.seasons import SeasonRepository
from football_data_manager.repository.repositories.teams import TeamRepository
from football_data_manager.repository.session import SessionFactory
from football_data_manager.syncer.dependency import SyncEntity
from football_data_manager.syncer.tasks.base import (
    AbstractSyncTask,
    SyncContext,
    SyncResult,
    append_unique,
)


logger = logging.getLogger(__name__)


class TeamSyncTask(AbstractSyncTask):
    """Sync teams and grounds for selected seasons."""

    def __init__(
        self,
        session_factory: SessionFactory,
        puller: TeamPuller,
        merger: TeamMerger,
        competition_repo: CompetitionRepository,
        season_repo: SeasonRepository,
        team_repo: TeamRepository,
    ):
        super().__init__(session_factory)
        self._puller = puller
        self._merger = merger
        self._competition_repo = competition_repo
        self._season_repo = season_repo
        self._team_repo = team_repo

    async def execute(self, context: SyncContext) -> SyncResult:
        result = SyncResult(entity=SyncEntity.TEAM.value)
        if not context.season_source_ids:
            logger.warning("No season_source_ids in context")
            result.errors += 1
            result.messages.append("No season_source_ids in context")
            return result

        total_seasons = len(context.season_source_ids)
        for season_idx, season_source_id in enumerate(context.season_source_ids, 1):
            logger.info(
                "Pulling teams for season %s (%d/%d)",
                season_source_id, season_idx, total_seasons,
            )
            season = await self._season_repo.get_by_pulselive_id(season_source_id)
            if season is None:
                logger.warning("Season '%s' not found in DB", season_source_id)
                result.errors += 1
                result.messages.append(f"Season '{season_source_id}' not found in DB")
                continue

            competition = await self._competition_repo.get_by_id(season.competition_id)
            if competition is None:
                logger.warning(
                    "Competition id '%s' not found for season", season.competition_id,
                )
                result.errors += 1
                result.messages.append(
                    f"Competition id '{season.competition_id}' not found for season"
                )
                continue

            raw_season_source_id = season.source_id.split("_")[-1]
            cursor: str | None = None
            page = 0

            while True:
                page += 1
                response = await self._puller.pull_teams(
                    competition.source_id,
                    raw_season_source_id,
                    limit=50,
                    _next=cursor,
                )
                if response.data:
                    logger.info(
                        "Merging %d teams (page %d)", len(response.data), page,
                    )
                    known_source_ids = {
                        str(item["id"])
                        for item in response.data
                        if await self._team_repo.get_by_pulselive_id(str(item["id"]))
                        is not None
                    }

                    filtered: V1TeamsResponse = response.model_copy(
                        update={"data": response.data}
                    )
                    teams, grounds = await self._merger.merge(
                        competition, season, filtered
                    )
                    for team in teams:
                        if team.source_id in known_source_ids:
                            result.updated += 1
                        else:
                            result.created += 1
                        append_unique(context.team_ids, team.id)
                        append_unique(context.team_source_ids, team.source_id)

                    for ground in grounds:
                        append_unique(context.ground_ids, ground.id)

                cursor = response.pagination.get("_next")
                if cursor is None:
                    break

        return result
