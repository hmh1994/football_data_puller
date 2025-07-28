from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.new_repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.new_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class PlayerRepository(PulseliveRepository[PlayerEntity]):
    """
    Player repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, PlayerEntity)

    async def load_championship_seasons(self, player: PlayerEntity) -> PlayerEntity:
        """
        Load championship seasons for the given player entity.
        This method uses lazy loading to fetch the championship seasons associated with the player entity.
        :param player: The player entity to load championship seasons for.
        :return: The player entity with championship seasons loaded.
        """
        return await self._load_lazy_fields(player, ["championship_seasons"])

    @BaseRepository.with_db_session
    async def get_birth_country_kr(
        self, session: AsyncSession, birth_country_en: str
    ) -> str:
        """
        Get the Korean name of a player's birth country by its English name.
        :param session: The database session.
        :param birth_country_en: The English name of the birth country.
        :return: The Korean name of the birth country, or None if not found.
        """
        stmt = (
            select(self.model)
            .where(self.model.birth_country_en == birth_country_en)
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalars().first().birth_country_kr if result else None

    @BaseRepository.with_db_session
    async def get_position_info_kr(
        self, session: AsyncSession, position_info_en: str
    ) -> str:
        """
        Get the Korean name of a player's position by its English name.
        :param session: The database session.
        :param position_info_en: The English name of the position.
        :return: The Korean name of the position, or None if not found.
        """
        stmt = (
            select(self.model)
            .where(self.model.position_info_en == position_info_en)
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalars().first().position_info_kr if result else None

    async def update_championship_season(
        self, player: PlayerEntity, season: SeasonEntity
    ) -> PlayerEntity:
        """
        Apply a championship season to the player.
        :param player: Player entity to update.
        :param season: Championship season entity to apply.
        :return: The updated player entity.
        """
        merged_player = await self.load_championship_seasons(player)
        season_id_list = [s.id for s in merged_player.championship_seasons]
        if season.id not in season_id_list:
            merged_player.championship_seasons.append(season)
        return merged_player

    async def read_by_display_name_en(self, name: str) -> PlayerEntity | None:
        """
        Reads a player entity by its display name in English.
        :param name: The display name in English.
        :return: The player entity if found, otherwise None.
        """
        return await self._read_one_by_field(display_name_en=name)

    async def read_by_full_name(self, name: str) -> PlayerEntity | None:
        """
        Reads a player entity by its full name.
        :param name: The full name of the player.
        :return: The player entity if found, otherwise None.
        """
        return await self._read_one_by_field(full_name=name)
