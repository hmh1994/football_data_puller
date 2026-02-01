from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.repositories.awards.award_entity import (
    AwardEntity,
)
from football_data_manager.common.repositories.player_stats.player_stat_award_association import (
    PlayerStatAwardAssociation,
)
from football_data_manager.common.repositories.player_stats.player_stat_entity import (
    PlayerStatEntity,
)
from football_data_manager.common.repositories.players.player_entity import PlayerEntity
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
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

    @PulseliveRepository.with_db_session
    async def read_by_player_season(
        self,
        session: AsyncSession,
        player: PlayerEntity,
        season: SeasonEntity,
    ) -> PlayerStatEntity | None:
        """
        Get player stat entity for specific player and season.

        Looks up player statistics for a given player in a specific season.
        This is used for associating awards with the correct player stat record.

        :param session: Database session
        :param player: Player entity
        :param season: Season entity
        :returns: Player stat entity or None if not found
        """
        stmt = select(PlayerStatEntity).where(
            PlayerStatEntity.player_id == player.id,
            PlayerStatEntity.season_id == season.id,
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    @PulseliveRepository.with_db_session
    async def read_by_player_season_id(
        self,
        session: AsyncSession,
        player_id: str,
        season_id: str,
    ) -> PlayerStatEntity | None:
        """
        Get player stat entity for specific player ID and season ID.

        Looks up player statistics for a given player in a specific season using IDs.

        :param session: Database session
        :param player_id: Player entity ID
        :param season_id: Season entity ID
        :returns: Player stat entity or None if not found
        """
        stmt = select(PlayerStatEntity).where(
            PlayerStatEntity.player_id == player_id,
            PlayerStatEntity.season_id == season_id,
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    @PulseliveRepository.with_db_session
    async def read_by_season(
        self,
        session: AsyncSession,
        season: SeasonEntity,
    ) -> list[PlayerStatEntity]:
        """
        Get all player stat entities for a specific season.

        Retrieves all player statistics for a given season.
        Used for calculating season-wide priors for score computation.

        :param session: Database session
        :param season: Season entity
        :returns: List of player stat entities for the season
        """
        stmt = select(PlayerStatEntity).where(
            PlayerStatEntity.season_id == season.id,
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def append_award_association(
        self, player_stat: PlayerStatEntity, award: AwardEntity, date: datetime
    ) -> PlayerStatEntity:
        """
        Append an award association to the player stat if it doesn't already exist.

        Uses efficient set-based duplicate checking with O(1) lookup performance.
        Automatically loads award associations and maintains chronological ordering by date.

        :param player_stat: Player stat entity to update
        :param award: Award entity to associate
        :param date: Date when the award was given
        :returns: Updated player stat entity with award association added if not duplicate
        """
        merged_player_stat = await self.load_award_associations(player_stat)

        # Efficient set-based duplicate checking with composite key (award_id, date) - O(1) lookup
        existing_awards = {
            (association.award_id, association.date)
            for association in merged_player_stat.award_associations
        }

        if (award.id, date) not in existing_awards:
            association = PlayerStatAwardAssociation(
                player_stat=merged_player_stat, award=award, date=date
            )
            merged_player_stat.award_associations.append(association)
            merged_player_stat.award_associations.sort(key=lambda s: s.date)

        return merged_player_stat

    async def upsert_player_stat(
        self, player_stat_entity: PlayerStatEntity
    ) -> PlayerStatEntity:
        """
        Create or update a player stat entity.

        Checks if a player stat already exists for the given player and season combination.
        If it exists, updates the existing entity with new values from the provided entity.
        If it doesn't exist, creates a new entity.

        :param player_stat_entity: Player stat entity to create or update
        :returns: Created or updated player stat entity
        """
        # Check if player stat already exists based on source_id from the entity
        existing_stat = await self.read_by_pulselive_id(player_stat_entity.source_id)

        if existing_stat:
            # Update existing player stat with new values from the provided entity
            existing_stat.number = player_stat_entity.number
            existing_stat.appearances = player_stat_entity.appearances
            existing_stat.defending_blocked = player_stat_entity.defending_blocked
            existing_stat.defending_duels_aerial_total = (
                player_stat_entity.defending_duels_aerial_total
            )
            existing_stat.defending_duels_aerial_won = (
                player_stat_entity.defending_duels_aerial_won
            )
            existing_stat.defending_duels_ground_total = (
                player_stat_entity.defending_duels_ground_total
            )
            existing_stat.defending_duels_ground_won = (
                player_stat_entity.defending_duels_ground_won
            )
            existing_stat.defending_duels_total = (
                player_stat_entity.defending_duels_total
            )
            existing_stat.defending_duels_won = player_stat_entity.defending_duels_won
            existing_stat.defending_fouls_committed = (
                player_stat_entity.defending_fouls_committed
            )
            existing_stat.defending_interceptions = (
                player_stat_entity.defending_interceptions
            )
            existing_stat.defending_possession_won_final_third = (
                player_stat_entity.defending_possession_won_final_third
            )
            existing_stat.defending_recoveries = player_stat_entity.defending_recoveries
            existing_stat.defending_tackles_total = (
                player_stat_entity.defending_tackles_total
            )
            existing_stat.defending_tackles_won = (
                player_stat_entity.defending_tackles_won
            )
            existing_stat.discipline_red_cards = player_stat_entity.discipline_red_cards
            existing_stat.discipline_red_cards_direct = (
                player_stat_entity.discipline_red_cards_direct
            )
            existing_stat.discipline_yellow_cards = (
                player_stat_entity.discipline_yellow_cards
            )
            existing_stat.goalkeeping_clean_sheets = (
                player_stat_entity.goalkeeping_clean_sheets
            )
            existing_stat.goalkeeping_goals_conceded = (
                player_stat_entity.goalkeeping_goals_conceded
            )
            existing_stat.goalkeeping_goals_prevented = (
                player_stat_entity.goalkeeping_goals_prevented
            )
            existing_stat.goalkeeping_high_claim = (
                player_stat_entity.goalkeeping_high_claim
            )
            existing_stat.goalkeeping_penalties_faced = (
                player_stat_entity.goalkeeping_penalties_faced
            )
            existing_stat.goalkeeping_penalty_goals_conceded = (
                player_stat_entity.goalkeeping_penalty_goals_conceded
            )
            existing_stat.goalkeeping_penalty_saved = (
                player_stat_entity.goalkeeping_penalty_saved
            )
            existing_stat.goalkeeping_saves = player_stat_entity.goalkeeping_saves
            existing_stat.passing_long_balls_accurate = (
                player_stat_entity.passing_long_balls_accurate
            )
            existing_stat.passing_long_balls_total = (
                player_stat_entity.passing_long_balls_total
            )
            existing_stat.passing_assists = player_stat_entity.passing_assists
            existing_stat.passing_chances_created = (
                player_stat_entity.passing_chances_created
            )
            existing_stat.passing_expected_assists = (
                player_stat_entity.passing_expected_assists
            )
            existing_stat.passing_passes_successful = (
                player_stat_entity.passing_passes_successful
            )
            existing_stat.passing_passes_total = player_stat_entity.passing_passes_total
            existing_stat.passing_crosses_successful = (
                player_stat_entity.passing_crosses_successful
            )
            existing_stat.passing_crosses_total = (
                player_stat_entity.passing_crosses_total
            )
            existing_stat.possession_dribble_total = (
                player_stat_entity.possession_dribble_total
            )
            existing_stat.possession_dribble_successful = (
                player_stat_entity.possession_dribble_successful
            )
            existing_stat.possession_fouls_won = player_stat_entity.possession_fouls_won
            existing_stat.possession_touches = player_stat_entity.possession_touches
            existing_stat.possession_touches_in_opposition_box = (
                player_stat_entity.possession_touches_in_opposition_box
            )
            existing_stat.shooting_expected_goals = (
                player_stat_entity.shooting_expected_goals
            )
            existing_stat.shooting_expected_goals_non_penalty = (
                player_stat_entity.shooting_expected_goals_non_penalty
            )
            existing_stat.shooting_expected_goals_on_target = (
                player_stat_entity.shooting_expected_goals_on_target
            )
            existing_stat.shooting_goals = player_stat_entity.shooting_goals
            existing_stat.shooting_goals_penalty = (
                player_stat_entity.shooting_goals_penalty
            )
            existing_stat.shooting_penalties_taken = (
                player_stat_entity.shooting_penalties_taken
            )
            existing_stat.shooting_shots = player_stat_entity.shooting_shots
            existing_stat.shooting_shots_on_target = (
                player_stat_entity.shooting_shots_on_target
            )
            existing_stat.minutes_played = player_stat_entity.minutes_played

            # Score fields
            existing_stat.score_shooting = player_stat_entity.score_shooting
            existing_stat.score_passing = player_stat_entity.score_passing
            existing_stat.score_defending = player_stat_entity.score_defending
            existing_stat.score_dribbling = player_stat_entity.score_dribbling
            existing_stat.score_discipline = player_stat_entity.score_discipline
            existing_stat.score_overall = player_stat_entity.score_overall

            return await self.update(existing_stat)
        else:
            # Create new player stat entity
            return await self.create(player_stat_entity)
