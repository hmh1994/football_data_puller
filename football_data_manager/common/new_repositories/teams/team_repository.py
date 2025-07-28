from football_data_manager.common.new_repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.new_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.new_repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.db.db_service import DbService


class TeamRepository(PulseliveRepository[TeamEntity]):
    """
    Team repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, TeamEntity)

    async def load_championship_seasons(self, team: TeamEntity) -> TeamEntity:
        """
        Load championship seasons for the given team entity.
        This method uses lazy loading to fetch the championship seasons associated with the team entity.
        :param team: The team entity to load championship seasons for.
        :return: The team entity with championship seasons loaded.
        """
        return await self._load_lazy_fields(team, ["championship_seasons"])

    async def update_championship_seasons(
        self, team: TeamEntity, season: SeasonEntity
    ) -> TeamEntity:
        """
        Update the team entity with the given championship season.
        This method checks if the championship season already exists in the team entity's championship seasons.
        :param team: The team entity to update.
        :param season: The season entity to append.
        :return: The updated team entity with the championship season appended if it did not already exist.
        """
        merged_team = await self.load_championship_seasons(team)
        season_id_list = [s.id for s in merged_team.championship_seasons]
        if season.id not in season_id_list:
            merged_team.championship_seasons.append(season)
        return merged_team

    async def read_by_abbreviation(self, abbreviation: str) -> TeamEntity | None:
        """
        Read the team entity by abbreviation.
        :param abbreviation: The abbreviation to get.
        :return: The team entity read by the given abbreviation.
        """
        return await self._read_one_by_field(abbreviation=abbreviation)
