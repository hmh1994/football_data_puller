from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.teams.team_championship_association import (
    TeamChampionshipAssociation,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.db.db_service import DbService


class TeamRepository(PulseliveRepository[TeamEntity]):
    """
    Repository for managing team entities with championship season associations.

    Provides specialized functionality for football teams including multilingual name lookups,
    championship season management, abbreviation-based searches, and team branding information.
    Extends PulseliveRepository for standard PULSELIVE source operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the team repository.

        :param db_service: Database service for database operations
        """
        super().__init__(db_service, TeamEntity)

    async def load_championship_seasons(self, team: TeamEntity) -> TeamEntity:
        """
        Load championship season associations for the given team entity.

        Uses lazy loading to fetch the championship season associations linked to the team.
        Loads the championship_season_associations relationship from the team entity.

        :param team: The team entity to load championship seasons for
        :returns: The team entity with championship season associations loaded
        """
        return await self._load_lazy_fields(
            team, [TeamChampionshipAssociation.SEASON_COLLECTION_NAME]
        )

    async def read_by_abbreviation(self, abbreviation: str) -> TeamEntity | None:
        """
        Read a team entity by its abbreviation code.

        Searches for a team using their abbreviation code which serves as a
        unique identifier for quick team identification.

        :param abbreviation: The team abbreviation code (e.g., 'MCI', 'LIV')
        :returns: The team entity if found, otherwise None
        """
        return await self._read_one_by_field(abbreviation=abbreviation)

    async def read_by_name_en(self, name: str) -> TeamEntity | None:
        """
        Read a team entity by its English name.

        Searches for a team using their full English name for identification.

        :param name: The full team name in English
        :returns: The team entity if found, otherwise None
        """
        return await self._read_one_by_field(name_en=name)

    async def read_by_short_name_en(self, name: str) -> TeamEntity | None:
        """
        Read a team entity by its English short name.

        Searches for a team using their abbreviated English name for identification.

        :param name: The short team name in English
        :returns: The team entity if found, otherwise None
        """
        return await self._read_one_by_field(short_name_en=name)

    async def update_championship_seasons(
        self, team: TeamEntity, season: SeasonEntity
    ) -> TeamEntity:
        """
        Apply a championship season association to the team.

        Creates or updates the association between a team and a championship season.
        Loads existing associations first, then adds the new season if not already present.

        :param team: Team entity to update
        :param season: Championship season entity to associate
        :returns: The updated team entity with new season association
        """
        merged_team = await self.load_championship_seasons(team)
        season_id_list = [
            s.season_id for s in merged_team.championship_season_associations
        ]
        if season.id not in season_id_list:
            association = TeamChampionshipAssociation(
                team=merged_team, season=season, date_end=season.date_end
            )
            merged_team.championship_season_associations.append(association)
        merged_team.championship_season_associations.sort(key=lambda s: s.date_end)
        return merged_team
