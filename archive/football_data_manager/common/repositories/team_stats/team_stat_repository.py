from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.matches.match_repository import (
    MatchRepository,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)
from football_data_manager.common.repositories.team_stats.team_stat_match_association import (
    TeamStatMatchAssociation,
)
from football_data_manager.common.services.db.db_service import DbService


class TeamStatRepository(PulseliveRepository[TeamStatEntity]):
    """
    Repository for managing team statistics entities and their fixture associations.

    Provides specialized functionality for handling team performance data including
    home, away, and overall statistics with fixture associations. Extends
    PulseliveRepository to inherit source-specific operations.
    """

    __match_repository: MatchRepository

    def __init__(self, db_service: DbService, match_repository: MatchRepository):
        super().__init__(db_service, TeamStatEntity)
        self.__match_repository = match_repository

    async def load_items(self, team_stat: TeamStatEntity) -> TeamStatEntity:
        """
        Load all team stat fixture association items (lazy-loaded relationships).

        Loads all fixture association collections for home, away, and overall
        statistics to enable proper manipulation and analysis.

        :param team_stat: The team stat entity to load items for
        :returns: The team stat entity with all fixture associations loaded
        """
        return await self._load_lazy_fields(
            team_stat,
            [
                TeamStatMatchAssociation.MATCH_COLLECTION_NAME,
            ],
        )

    @PulseliveRepository.with_db_session
    async def clear_match_associations(
        self,
        session: AsyncSession,
        team_stat: TeamStatEntity,
    ) -> None:
        """
        Clear all match associations for a team stat entity from the database.

        Deletes all TeamStatMatchAssociation records associated with the given
        team stat entity. This is used for force reset operations to ensure
        clean rebuild of statistics.

        :param session: Database session (injected by decorator)
        :param team_stat: The team stat entity to clear associations for
        """
        from sqlalchemy import delete

        stmt = delete(TeamStatMatchAssociation).where(
            TeamStatMatchAssociation.team_stat_id == team_stat.id
        )
        await session.execute(stmt)

    async def read_by_season(self, season: SeasonEntity) -> list[TeamStatEntity]:
        """
        Read team statistics for a specific season.

        Retrieves all team statistics entities associated with the given season,
        providing comprehensive season-wide performance data.

        :param season: Season entity to filter team statistics
        :returns: List of team statistics entities for the specified season
        """
        return await self._read_by_field(season_id=season.id)

    async def append_fixtures(
        self,
        team_stat: TeamStatEntity,
        kickoff_time: datetime,
        match: MatchEntity,
        is_appending: bool = False,
    ) -> TeamStatEntity:
        if (
            match.away_team_id != team_stat.team_id
            and match.home_team_id != team_stat.team_id
        ):
            raise ValueError(
                f"Team {team_stat.team_id} does not match match {match.id} association"
            )

        if match.period != PeriodEnum.FULLTIME:
            return team_stat

        # Only load items if not already loaded (check if match_associations is accessible)
        # Avoid reloading which would discard in-memory changes
        if not hasattr(team_stat, '_associations_loaded') or not team_stat._associations_loaded:
            team_stat = await self.load_items(team_stat)
            team_stat._associations_loaded = True

        if team_stat.match_associations:
            # Check for duplicate
            if any(match.id == m.match_id for m in team_stat.match_associations):
                return team_stat

            last_match = team_stat.match_associations[-1]
            if kickoff_time <= last_match.kickoff_time:
                if is_appending:
                    raise RuntimeError(
                        f"Match {match.id} already fixing but nested fix is called."
                    )
                matches_data = [
                    (m.match_id, m.kickoff_time) for m in team_stat.match_associations
                ]
                matches_data.append((match.id, kickoff_time))
                matches_data.sort(key=lambda m: m[1])
                team_stat.reset_statistics()
                team_stat._associations_loaded = True  # Keep flag after reset
                for match_id, kickoff in matches_data:
                    match_entity = await self.__match_repository.read_by_id(match_id)
                    if match_entity:
                        team_stat = await self.append_fixtures(
                            team_stat, kickoff, match_entity, is_appending=True
                        )
                return team_stat  # Return after rebuilding to avoid double-append

        team_stat.match_associations.append(
            TeamStatMatchAssociation(
                team_stat=team_stat,
                match=match,
                kickoff_time=kickoff_time,
                is_home=match.home_team_id == team_stat.team_id,
            )
        )

        # Update goals and points
        is_home = team_stat.check_is_home_match(match)
        team_stat.update_match_result(
            is_home=is_home,
            team_score=match.home_team_score if is_home else match.away_team_score,
            opponent_score=match.away_team_score if is_home else match.home_team_score,
        )

        return team_stat

    class __TeamStatComparator:
        target: TeamStatEntity
        home: MatchEntity | None
        away: MatchEntity | None

        def __init__(
            self,
            target: TeamStatEntity,
            home: MatchEntity | None = None,
            away: MatchEntity | None = None,
        ) -> None:
            """
            Initialize a comparator for team statistics.

            :param target: The target team stat entity to compare against
            :param home: Optional home match entity for head-to-head comparison
            :param away: Optional away match entity for head-to-head comparison
            """
            self.target = target
            self.home = home
            self.away = away

    async def update_position(
        self,
        target_team_stat: TeamStatEntity,
        other_team_stats: list[TeamStatEntity],
    ) -> TeamStatEntity:
        """
        Update team standings positions based on comparison with other teams.

        Calculates overall, home, and away positions by comparing the target team's
        statistics against all other teams in the same season. Uses football ranking
        criteria: points, goal difference, goals scored, and head-to-head results.

        :param target_team_stat: The team stat entity to update positions for
        :param other_team_stats: List of other team stat entities to compare against
        :returns: The updated team stat entity with refreshed position values
        """
        # Load target team associations for head-to-head comparisons
        target_team_stat = await self.load_items(target_team_stat)

        # Filter to only teams from the same season, excluding the target team
        comparable_teams = {
            team_stat.team_id: self.__TeamStatComparator(team_stat, None, None)
            for team_stat in other_team_stats
            if team_stat.team_id != target_team_stat.team_id
            and team_stat.season_id == target_team_stat.season_id
        }

        matches: list[MatchEntity] = []
        for m in target_team_stat.match_associations:
            matches.append(await self.__match_repository.read_by_id(m.match_id))
        for match in matches:
            if target_team_stat.check_is_home_match(match):
                comparable_teams[match.away_team_id].home = match
            elif target_team_stat.check_is_away_match(match):
                comparable_teams[match.home_team_id].away = match
            else:
                raise ValueError(
                    f"Match {match.id} does not belong to target team {target_team_stat.team_id}"
                )

        # Calculate positions by counting teams that rank lower (comparison >= 0)
        overall_comparisons = []
        home_comparisons = []
        away_comparisons = []

        for other_team in comparable_teams.values():
            overall_comparisons.append(
                target_team_stat.compare_overall(
                    other_team.target, other_team.home, other_team.away
                )
            )
            home_comparisons.append(target_team_stat.compare_home(other_team.target))
            away_comparisons.append(target_team_stat.compare_away(other_team.target))

        # Position = number of teams that rank lower + 1
        target_team_stat.overall_position = (
            sum(comp < 0 for comp in overall_comparisons) + 1
        )
        target_team_stat.home_position = sum(comp < 0 for comp in home_comparisons) + 1
        target_team_stat.away_position = sum(comp < 0 for comp in away_comparisons) + 1

        return target_team_stat
