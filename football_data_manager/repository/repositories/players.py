from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.player_championship_association import PlayerChampionshipAssociation
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class PlayerRepository(PulseliveRepository[PlayerEntity]):
    """Repository for player entities with championship management."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, PlayerEntity)

    async def load_championship_seasons(
        self, player: PlayerEntity
    ) -> PlayerEntity:
        """
        Load championship season associations for the player.

        :param player: Player entity
        :return: Player with championship seasons loaded
        """
        return await self._load_lazy_fields(
            player,
            [PlayerChampionshipAssociation.SEASON_COLLECTION_NAME],
        )

    async def get_nationality_kr(self, nationality_en: str) -> str | None:
        """
        Get Korean nationality name by English name.

        :param nationality_en: English nationality name
        :return: Korean nationality name or None
        """
        result = await self._get_one_by_field(nationality_en=nationality_en)
        return result.nationality_kr if result else None

    async def append_championship_season(
        self, player: PlayerEntity, season: SeasonEntity
    ) -> PlayerEntity:
        """
        Append a championship season if not already associated.

        :param player: Player entity
        :param season: Season entity to associate
        :return: Updated player entity
        """
        merged = await self.load_championship_seasons(player)
        existing_ids = {
            a.season_id for a in merged.championship_season_associations
        }
        if season.id not in existing_ids:
            assoc = PlayerChampionshipAssociation(
                player=merged, season=season, date_end=season.date_end
            )
            merged.championship_season_associations.append(assoc)
        merged.championship_season_associations.sort(key=lambda s: s.date_end)
        return merged

    async def get_by_display_name_en(self, name: str) -> PlayerEntity | None:
        """
        Get player by English display name.

        :param name: English display name
        :return: Player entity or None
        """
        return await self._get_one_by_field(display_name_en=name)

    async def get_by_full_name(self, name: str) -> PlayerEntity | None:
        """
        Get player by full legal name.

        :param name: Full name
        :return: Player entity or None
        """
        return await self._get_one_by_field(full_name=name)

    async def get_by_ids(
        self, ids: list[str], session: AsyncSession | None = None
    ) -> list[PlayerEntity]:
        """
        Get multiple players by IDs.

        :param ids: List of player UUIDs
        :param session: Optional existing session
        :return: List of player entities
        """
        if not ids:
            return []

        async def _do(s: AsyncSession) -> list[PlayerEntity]:
            stmt = select(PlayerEntity).where(PlayerEntity.id.in_(ids))
            result = await s.execute(stmt)
            return list(result.scalars().all())

        if session:
            return await _do(session)
        return await self._execute_with_retry(_do)
