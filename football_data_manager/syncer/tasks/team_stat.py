import logging

from football_data_manager.merger.mergers.team_stat import TeamStatMerger
from football_data_manager.repository.entities.team_stats import TeamStatEntity
from football_data_manager.repository.repositories.competitions import (
    CompetitionRepository,
)
from football_data_manager.repository.repositories.fixtures import FixtureRepository
from football_data_manager.repository.repositories.grounds import GroundRepository
from football_data_manager.repository.repositories.seasons import SeasonRepository
from football_data_manager.repository.repositories.team_stats import TeamStatRepository
from football_data_manager.repository.repositories.teams import TeamRepository
from football_data_manager.repository.session import SessionFactory
from football_data_manager.syncer.dependency import SyncEntity
from football_data_manager.syncer.tasks.base import (
    AbstractSyncTask,
    SyncContext,
    SyncResult,
    is_updated_within,
)


logger = logging.getLogger(__name__)


class TeamStatSyncTask(AbstractSyncTask):
    """Sync team-season statistics (derived + API-enriched)."""

    def __init__(
        self,
        session_factory: SessionFactory,
        merger: TeamStatMerger,
        competition_repo: CompetitionRepository,
        season_repo: SeasonRepository,
        team_repo: TeamRepository,
        fixture_repo: FixtureRepository,
        ground_repo: GroundRepository,
        team_stat_repo: TeamStatRepository,
    ):
        super().__init__(session_factory)
        self._merger = merger
        self._competition_repo = competition_repo
        self._season_repo = season_repo
        self._team_repo = team_repo
        self._fixture_repo = fixture_repo
        self._ground_repo = ground_repo
        self._team_stat_repo = team_stat_repo

    async def execute(self, context: SyncContext) -> SyncResult:
        result = SyncResult(entity=SyncEntity.TEAM_STAT.value)
        if not context.season_source_ids or not context.competition_source_ids:
            logger.warning("Missing competition/season context for team-stat sync")
            result.errors += 1
            result.messages.append(
                "Missing competition/season context for team-stat sync"
            )
            return result
        if not context.team_ids:
            logger.warning("No team_ids in context")
            result.skipped += 1
            result.messages.append("No team_ids in context")
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

        total_teams = len(context.team_ids)
        for idx, team_id in enumerate(context.team_ids, 1):
            team = await self._team_repo.get_by_id(team_id)
            if team is None:
                result.errors += 1
                result.messages.append(f"Team id '{team_id}' not found")
                continue

            logger.info(
                "Processing team stat for %s (%d/%d)",
                team.name_en or team_id, idx, total_teams,
            )

            existing = await self._team_stat_repo.get_by_pulselive_id(
                TeamStatEntity.get_source_id(season, team)
            )
            if existing and is_updated_within(existing):
                result.skipped += 1
                continue

            ground = None
            fixtures = await self._fixture_repo.get_by_team_on_season(season, team)
            for fixture in fixtures:
                if fixture.ground_id:
                    ground = await self._ground_repo.get_by_id(fixture.ground_id)
                    if ground is not None:
                        break

            merged = await self._merger.merge(team, competition, season, ground)
            if merged is None:
                result.skipped += 1
                continue
            if existing is None:
                result.created += 1
            else:
                result.updated += 1

        return result
