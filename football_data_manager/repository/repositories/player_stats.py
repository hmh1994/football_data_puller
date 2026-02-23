from datetime import datetime

from football_data_manager.repository.entities.awards import AwardEntity
from football_data_manager.repository.entities.player_stat_award_association import (
    PlayerStatAwardAssociation,
)
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class PlayerStatRepository(PulseliveRepository[PlayerStatEntity]):
    """Repository for player stat entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, PlayerStatEntity)

    async def load_award_associations(
        self, player_stat: PlayerStatEntity
    ) -> PlayerStatEntity:
        """Load award associations for player stat."""
        return await self._load_lazy_fields(
            player_stat,
            [PlayerStatAwardAssociation.AWARD_COLLECTION_NAME],
        )

    async def get_by_player_season(
        self, player: PlayerEntity, season: SeasonEntity
    ) -> PlayerStatEntity | None:
        """Get player stat by player and season."""
        return await self._get_one_by_field(player_id=player.id, season_id=season.id)

    async def append_award_association(
        self,
        player_stat: PlayerStatEntity,
        award: AwardEntity,
        date: datetime,
    ) -> PlayerStatEntity:
        """Append player-stat-award association if not already present."""
        merged = await self.load_award_associations(player_stat)
        exists = any(
            assoc.award_id == award.id and assoc.date == date
            for assoc in merged.award_associations
        )
        if not exists:
            merged.award_associations.append(
                PlayerStatAwardAssociation(player_stat=merged, award=award, date=date)
            )
            merged.award_associations.sort(key=lambda assoc: assoc.date)
        return merged
