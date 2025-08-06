from datetime import datetime

from football_data_manager.common.repositories.awards.award_entity import (
    AwardEntity,
)
from football_data_manager.common.repositories.player_stats.player_stat_award_association import (
    PlayerStatAwardAssociation,
)
from football_data_manager.common.repositories.player_stats.player_stat_entity import (
    PlayerStatEntity,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class PlayerStatRepository(PulseliveRepository[PlayerStatEntity]):
    """
    Player statistics repository.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, PlayerStatEntity)

    async def load_award_associations(
        self, player_stat: PlayerStatEntity
    ) -> PlayerStatEntity:
        """
        Load award associations for the given player stat entity.
        This method uses lazy loading to fetch the award associations with the player stat entity.
        :param player_stat: The player stat entity to load award associations for.
        :return: The player stat entity with award associations loaded.
        """
        return await self._load_lazy_fields(
            player_stat, [PlayerStatAwardAssociation.AWARD_COLLECTION_NAME]
        )

    async def append_award(
        self, player_stat: PlayerStatEntity, award: AwardEntity, date: datetime
    ) -> PlayerStatEntity:
        """
        Update the player stat with the given award.
        This method checks if the award already exists in the player stat's award associations.
        :param player_stat: The player stat entity to update.
        :param award: The award entity to append.
        :param date: The date associated with the award.
        :return: The updated player stat entity with the award appended if it did not already exist.
        """
        merged_player_stat = await self.load_award_associations(player_stat)
        award_id_list = [
            association.award_id
            for association in merged_player_stat.award_associations
        ]
        if award.id not in award_id_list:
            association = PlayerStatAwardAssociation(
                player_stat=merged_player_stat, award=award, date=date
            )
            merged_player_stat.award_associations.append(association)
        merged_player_stat.award_associations.sort(key=lambda s: s.date)
        return merged_player_stat
