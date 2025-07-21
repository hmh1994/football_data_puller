from football_data_manager.common.new_repositories.awards.award_entity import (
    AwardEntity,
)
from football_data_manager.common.new_repositories.base_repository import BaseRepository
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

    async def load_awards(self, player_stat: PlayerStatEntity) -> PlayerStatEntity:
        """
        Load awards for the given player stat entity.
        This method uses lazy loading to fetch the awards associated with the player stat entity.
        :param player_stat: The player stat entity to load awards for.
        :return: The player stat entity with awards loaded.
        """
        return await self._load_lazy_fields(player_stat, ["awards"])

    async def update_award(
        self, player_stat: PlayerStatEntity, award: AwardEntity
    ) -> PlayerStatEntity:
        """
        Update the player stat with the given award.
        This method checks if the award already exists in the player stat's awards.
        :param player_stat: The player stat entity to update.
        :param award: The award entity to append.
        :return: The updated player stat entity with the award appended if it did not already exist.
        """
        merged_player_stat = await self.load_awards(player_stat)
        award_id_list = [a.id for a in merged_player_stat.awards]
        if award.id not in award_id_list:
            merged_player_stat.awards.append(award)
        return merged_player_stat
