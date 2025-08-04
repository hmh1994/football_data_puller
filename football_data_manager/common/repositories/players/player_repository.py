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
    championship season management, and position/birth country information retrieval.
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

    async def get_birth_country_kr(self, birth_country_en: str) -> str | None:
        """
        Get the Korean name of a player's birth country by its English name.

        Searches for a player with the specified English birth country name
        and returns the corresponding Korean birth country name.

        :param birth_country_en: The English name of the birth country
        :returns: The Korean name of the birth country, or None if not found
        """
        result = await self._read_one_by_field(birth_country_en=birth_country_en)
        return result.birth_country_kr if result else None

    async def get_position_info_kr(self, position_info_en: str) -> str:
        """
        Get the Korean name of a player's position by its English name.

        Searches for a player with the specified English position information
        and returns the corresponding Korean position information.

        :param position_info_en: The English name of the position
        :returns: The Korean name of the position, or None if not found
        """
        result = await self._read_one_by_field(position_info_en=position_info_en)
        return result.position_info_kr if result else None

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
            s.season.id for s in merged_player.championship_season_associations
        ]
        if season.id not in season_id_list:
            association = PlayerChampionshipAssociation(
                player=merged_player, season=season, date_end=season.date_end
            )
            merged_player.championship_season_associations.append(association)
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
