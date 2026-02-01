from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.entities.team_championship_association import TeamChampionshipAssociation
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class TeamRepository(PulseliveRepository[TeamEntity]):
    """Repository for team entities with championship management."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, TeamEntity)

    async def load_championship_seasons(
        self, team: TeamEntity
    ) -> TeamEntity:
        """
        Load championship season associations for the team.

        :param team: Team entity
        :return: Team with championship seasons loaded
        """
        return await self._load_lazy_fields(
            team,
            [TeamChampionshipAssociation.SEASON_COLLECTION_NAME],
        )

    async def get_by_abbreviation(self, abbreviation: str) -> TeamEntity | None:
        """
        Get team by abbreviation code.

        :param abbreviation: Team abbreviation
        :return: Team entity or None
        """
        return await self._get_one_by_field(abbreviation=abbreviation)

    async def get_by_name_en(self, name: str) -> TeamEntity | None:
        """
        Get team by English name.

        :param name: English name
        :return: Team entity or None
        """
        return await self._get_one_by_field(name_en=name)

    async def get_by_short_name_en(self, name: str) -> TeamEntity | None:
        """
        Get team by English short name.

        :param name: English short name
        :return: Team entity or None
        """
        return await self._get_one_by_field(short_name_en=name)

    async def append_championship_season(
        self, team: TeamEntity, season: SeasonEntity
    ) -> TeamEntity:
        """
        Append a championship season if not already associated.

        :param team: Team entity
        :param season: Season entity to associate
        :return: Updated team entity
        """
        merged = await self.load_championship_seasons(team)
        existing_ids = {
            a.season_id for a in merged.championship_season_associations
        }
        if season.id not in existing_ids:
            assoc = TeamChampionshipAssociation(
                team=merged, season=season, date_end=season.date_end
            )
            merged.championship_season_associations.append(assoc)
        merged.championship_season_associations.sort(key=lambda s: s.date_end)
        return merged
