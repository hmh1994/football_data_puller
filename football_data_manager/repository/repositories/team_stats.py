from datetime import datetime

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.team_stats import TeamStatEntity
from football_data_manager.repository.entities.team_stat_match_association import TeamStatMatchAssociation
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class TeamStatRepository(PulseliveRepository[TeamStatEntity]):
    """Repository for team stat entities with match association management."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, TeamStatEntity)

    async def load_items(self, team_stat: TeamStatEntity) -> TeamStatEntity:
        """
        Load all team stat match association items (lazy-loaded relationships).

        :param team_stat: Team stat entity
        :return: Team stat with match associations loaded
        """
        return await self._load_lazy_fields(
            team_stat,
            [TeamStatMatchAssociation.MATCH_COLLECTION_NAME],
        )

    async def get_by_season(
        self,
        season: SeasonEntity,
        session: AsyncSession | None = None,
    ) -> list[TeamStatEntity]:
        """
        Get team statistics for a specific season.

        :param season: Season entity
        :param session: Optional existing session
        :return: List of team stat entities
        """
        async def _do(s: AsyncSession) -> list[TeamStatEntity]:
            results = await self._get_by_field(s, season_id=season.id)
            return results

        if session:
            return await _do(session)
        return await self._execute_with_retry(_do)

    async def clear_match_associations(
        self,
        team_stat: TeamStatEntity,
        session: AsyncSession | None = None,
    ) -> None:
        """
        Clear all match associations for a team stat entity.

        :param team_stat: Team stat entity
        :param session: Optional existing session
        """
        async def _do(s: AsyncSession) -> None:
            stmt = delete(TeamStatMatchAssociation).where(
                TeamStatMatchAssociation.team_stat_id == team_stat.id
            )
            await s.execute(stmt)

        if session:
            return await _do(session)
        return await self._execute_with_retry(_do)

    async def append_match(
        self,
        team_stat: TeamStatEntity,
        match: MatchEntity,
        kickoff_time: datetime,
    ) -> TeamStatEntity:
        """
        Append a match association to the team stat if not already present.

        :param team_stat: Team stat entity
        :param match: Match entity to associate
        :param kickoff_time: Match kickoff time
        :return: Updated team stat entity
        """
        merged = await self.load_items(team_stat)

        if any(m.match_id == match.id for m in merged.match_associations):
            return merged

        is_home = match.home_team_id == team_stat.team_id

        merged.match_associations.append(
            TeamStatMatchAssociation(
                team_stat=merged,
                match=match,
                kickoff_time=kickoff_time,
                is_home=is_home,
            )
        )
        merged.match_associations.sort(key=lambda m: m.kickoff_time)
        return merged
