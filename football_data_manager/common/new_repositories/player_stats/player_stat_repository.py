from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.new_repositories.awards.award_entity import (
    AwardEntity,
)
from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.player_stats.player_stat_award_association import (
    PlayerStatAwardAssociation,
)
from football_data_manager.common.new_repositories.player_stats.player_stat_entity import (
    PlayerStatEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class PlayerStatRepository(BaseRepository[PlayerStatEntity]):
    """
    Player statistics repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, PlayerStatEntity)

    @BaseRepository.with_db_session
    async def load_lazy_fields(
        self, session: AsyncSession, player_stat: PlayerStatEntity
    ) -> PlayerStatEntity:
        """
        Load lazy fields for the player stat entity.
        Fields for lazy loading include `awards`.
        :param session: The database session.
        :param player_stat: The player stat entity to load lazy fields for.
        :return: The player stat entity with lazy fields loaded.
        """
        merged_entity = await session.merge(player_stat)
        await session.refresh(
            merged_entity,
            attribute_names=[PlayerStatAwardAssociation.AWARD_COLLECTION_NAME],
        )
        return merged_entity

    @BaseRepository.with_db_session
    async def update_award(
        self, session: AsyncSession, player_stat: PlayerStatEntity, award: AwardEntity
    ) -> PlayerStatEntity:
        await self.load_lazy_fields(session, player_stat)
        award_id_list = [a.id for a in player_stat.awards]
        if award in award_id_list:
            # If the award already exists, we do not need to update it
            return player_stat
        else:
            # If the award does not exist, we add the award to the player stat with creating a new association
            player_stat.awards.append(award)
            return player_stat
