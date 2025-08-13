from football_data_manager.common.repositories.players.player_championship_association import (
    PlayerChampionshipAssociation,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class PlayerRepository(PulseliveRepository[PlayerEntity]):
    """
    Repository for managing player entities with championship season associations.

    Provides specialized functionality for football players including multilingual name lookups,
    championship season management, and position/nationality information retrieval.
    Extends PulseliveRepository for standard PULSELIVE source operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the player repository.

        :param db_service: Database service for database operations
        """
        super().__init__(db_service, PlayerEntity)

    async def load_championship_seasons(self, player: PlayerEntity) -> PlayerEntity:
        """
        Load championship season associations for the given player entity.

        Uses lazy loading to fetch the championship season associations linked to the player.
        Loads the championship_season_associations relationship from the player entity.

        :param player: The player entity to load championship seasons for
        :returns: The player entity with championship season associations loaded
        """
        return await self._load_lazy_fields(
            player, [PlayerChampionshipAssociation.SEASON_COLLECTION_NAME]
        )

    async def get_nationality_kr(self, nationality_en: str) -> str | None:
        """
        Get the Korean name of a player's nationality by its English name.

        Searches for a player with the specified English nationality name
        and returns the corresponding Korean nationality name.

        :param nationality_en: The English name of the nationality
        :returns: The Korean name of the nationality, or None if not found
        """
        result = await self._read_one_by_field(nationality_en=nationality_en)
        return result.nationality_kr if result else None

    async def update_championship_season(
        self, player: PlayerEntity, season: SeasonEntity
    ) -> PlayerEntity:
        """
        Apply a championship season association to the player.

        Creates or updates the association between a player and a championship season.
        Loads existing associations first, then adds the new season if not already present.

        :param player: Player entity to update
        :param season: Championship season entity to associate
        :returns: The updated player entity with new season association
        """
        merged_player = await self.load_championship_seasons(player)
        season_id_list = [
            s.season_id for s in merged_player.championship_season_associations
        ]
        if season.id not in season_id_list:
            association = PlayerChampionshipAssociation(
                player=merged_player, season=season, date_end=season.date_end
            )
            merged_player.championship_season_associations.append(association)
        merged_player.championship_season_associations.sort(key=lambda s: s.date_end)
        return merged_player

    async def read_by_display_name_en(self, name: str) -> PlayerEntity | None:
        """
        Read a player entity by its English display name.

        Searches for a player using their English display name which serves
        as a unique identifier in the system.

        :param name: The English display name of the player
        :returns: The player entity if found, otherwise None
        """
        return await self._read_one_by_field(display_name_en=name)

    async def read_by_full_name(self, name: str) -> PlayerEntity | None:
        """
        Read a player entity by its full legal name.

        Searches for a player using their complete legal name as recorded
        in the system.

        :param name: The full legal name of the player
        :returns: The player entity if found, otherwise None
        """
        return await self._read_one_by_field(full_name=name)
