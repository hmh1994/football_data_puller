from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.repositories.base_repository import BaseRepository
from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.repositories.matches.match_card_association import (
    MatchCardAssociation,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.matches.match_goal_association import (
    MatchGoalAssociation,
)
from football_data_manager.common.repositories.matches.match_lineup_association import (
    MatchLineupAssociation,
)
from football_data_manager.common.repositories.matches.match_substitute_association import (
    MatchSubstituteAssociation,
)
from football_data_manager.common.repositories.matches.match_substitution_association import (
    MatchSubstitutionAssociation,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.services.db.db_service import DbService


class MatchRepository(PulseliveRepository[MatchEntity]):
    """
    Repository for managing match entities and their associations.

    Provides specialized functionality for handling complex match data including
    lineups, events, substitutions, and various match-related associations.
    Extends PulseliveRepository to inherit source-specific operations.
    """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, MatchEntity)

    async def load_items(self, match: MatchEntity) -> MatchEntity:
        """
        Load all match association items (lazy-loaded relationships).

        Loads all association collections including cards, goals, lineups,
        substitutes, and substitutions for both home and away teams.

        :param match: The match entity to load items for
        :returns: The match entity with all associations loaded
        """
        return await self._load_lazy_fields(
            match,
            [
                MatchCardAssociation.CARD_INFO_COLLECTION_NAME,
                MatchGoalAssociation.GOAL_INFO_COLLECTION_NAME,
                MatchLineupAssociation.POSITION_COLLECTION_NAME,
                MatchSubstituteAssociation.PLAYER_INFO_COLLECTION_NAME,
                MatchSubstitutionAssociation.SUBSTITUTION_COLLECTION_NAME,
            ],
        )

    async def read_by_fixture(self, fixture: FixtureEntity) -> MatchEntity:
        """
        Read a match by its associated fixture.

        :param fixture: The fixture entity to filter by
        :returns: The match entity associated with the given fixture
        """
        return await self._read_one_by_field(fixture_id=fixture.id)

    @BaseRepository.with_db_session
    async def read_by_team_on_season(
        self,
        session: AsyncSession,
        season: SeasonEntity,
        team: TeamEntity,
        **kwargs,
    ) -> list[MatchEntity]:
        """
        Read matches for a specific team in a given season.

        Retrieves all matches where the specified team is either home or away team
        within the given season. The method joins with fixture entities to filter
        by season and then filters by team participation (home or away).

        :param session: Database session for the query
        :param season: Season entity to filter matches
        :param team: Team entity to filter matches (home or away)
        :param kwargs: Field names and values to filter by.
        :returns: List of match entities for the team in the specified season
        """
        # Build query to join MatchEntity with FixtureEntity and filter by season and team
        stmt = (
            select(MatchEntity)
            .filter_by(**kwargs)
            .join(FixtureEntity, MatchEntity.fixture_id == FixtureEntity.id)
            .where(
                (FixtureEntity.season_id == season.id)
                & (
                    or_(
                        MatchEntity.home_team_id == team.id,
                        MatchEntity.away_team_id == team.id,
                    )
                )
            )
            .order_by(FixtureEntity.game_week)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    @BaseRepository.with_db_session
    async def read_by_season(
        self, session: AsyncSession, season: SeasonEntity
    ) -> list[MatchEntity]:
        """
        Read all matches for a given season.

        Retrieves all matches within the specified season by joining with fixture entities
        to filter by season, ordered by game week for chronological ordering.

        :param session: Database session for the query
        :param season: Season entity to filter matches
        :returns: List of match entities for the specified season
        """
        # Build query to join MatchEntity with FixtureEntity and filter by season
        stmt = (
            select(MatchEntity)
            .join(FixtureEntity, MatchEntity.fixture_id == FixtureEntity.id)
            .where(FixtureEntity.season_id == season.id)
            .order_by(FixtureEntity.game_week)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def append_card(
        self,
        match: MatchEntity,
        is_home: bool,
        player: PlayerEntity,
        index: int,
        card_type: CardTypeEnum,
        clock: int,
    ) -> MatchEntity:
        merged_match = await self.load_items(match)
        target_list = merged_match.card_associations

        # Check for duplicate using more efficient set comparison
        existing_cards = {
            (c.player_id, c.card_type, c.clock, c.is_home) for c in target_list
        }
        card_key = (player.id, card_type, clock, is_home)

        if card_key not in existing_cards:
            card_association = MatchCardAssociation(
                match=merged_match,
                player=player,
                index=index,
                card_type=card_type,
                clock=clock,
                is_home=is_home,
            )
            target_list.append(card_association)
        target_list.sort(key=lambda c: c.clock)
        return merged_match

    async def append_goal(
        self,
        match: MatchEntity,
        is_home: bool,
        player: PlayerEntity,
        assist_player: PlayerEntity | None,
        index: int,
        is_penalty: bool,
        is_own_goal: bool,
        clock: int,
    ) -> MatchEntity:
        """
        Append a goal to the match if it doesn't already exist.

        Args:
            match: The match entity
            is_home: Whether the goal is for the home team
            player: The player who scored the goal
            assist_player: The player who assisted (optional)
            is_penalty: Whether it was a penalty goal
            is_own_goal: Whether it was an own goal
            clock: The time when the goal was scored

        Returns:
            The updated match entity with the goal added
        """
        merged_match = await self.load_items(match)
        target_list = merged_match.goal_associations

        # Check for duplicate using more efficient set comparison
        existing_goals = {(g.player_id, g.clock, g.is_home) for g in target_list}
        goal_key = (player.id, clock, is_home)

        if goal_key not in existing_goals:
            goal_association = MatchGoalAssociation(
                match=merged_match,
                player=player,
                assist_player=assist_player,
                index=index,
                clock=clock,
                is_penalty=is_penalty,
                is_own_goal=is_own_goal,
                is_home=is_home,
            )
            target_list.append(goal_association)
        target_list.sort(key=lambda g: g.clock)
        return merged_match

    async def append_lineup(
        self,
        match: MatchEntity,
        is_home: bool,
        player: PlayerEntity,
        position: PositionEnum,
        shirt_number: int,
        row: int,
        column: int,
    ) -> MatchEntity:
        """
        Append a player to the starting lineup if not already present.

        Args:
            match: The match entity
            is_home: Whether the player is for the home team
            player: The player entity
            shirt_number: The player's shirt number
            row: Formation row position
            column: Formation column position

        Returns:
            The updated match entity with the lineup player added
        """
        merged_match = await self.load_items(match)
        target_list = merged_match.lineup_associations

        # Check for duplicate using more efficient set comparison
        existing_players = {(l.player_id, l.is_home) for l in target_list}

        if (player.id, is_home) not in existing_players:
            lineup_association = MatchLineupAssociation(
                match=merged_match,
                player=player,
                position=position,
                shirt_number=shirt_number,
                row=row,
                column=column,
                is_home=is_home,
            )
            target_list.append(lineup_association)
        target_list.sort(key=lambda l: (l.is_home, l.row, l.column))
        return merged_match

    async def append_substitute(
        self,
        match: MatchEntity,
        is_home: bool,
        player: PlayerEntity,
        position: PositionEnum,
        shirt_number: int,
    ) -> MatchEntity:
        """
        Append a substitute player if not already present.

        Args:
            match: The match entity
            is_home: Whether the substitute is for the home team
            player: The substitute player entity
            shirt_number: The player's shirt number

        Returns:
            The updated match entity with the substitute added
        """
        merged_match = await self.load_items(match)
        target_list = merged_match.substitute_associations

        # Check for duplicate using more efficient set comparison
        existing_players = {(s.player_id, s.is_home) for s in target_list}

        if (player.id, is_home) not in existing_players:
            substitute_association = MatchSubstituteAssociation(
                match=merged_match,
                player=player,
                position=position,
                shirt_number=shirt_number,
                is_home=is_home,
            )
            target_list.append(substitute_association)
        target_list.sort(key=lambda s: (s.is_home, s.shirt_number))
        return merged_match

    async def append_substitution(
        self,
        match: MatchEntity,
        is_home: bool,
        in_player: PlayerEntity,
        out_player: PlayerEntity,
        clock: int,
    ) -> MatchEntity:
        """
        Append a substitution if it doesn't already exist.

        Args:
            match: The match entity
            is_home: Whether the substitution is for the home team
            in_player: The player coming in
            out_player: The player going out
            clock: The time when the substitution occurred

        Returns:
            The updated match entity with the substitution added
        """
        merged_match = await self.load_items(match)
        target_list = merged_match.substitution_associations

        # Check for duplicate using more efficient set comparison
        existing_substitutions = {
            (s.in_player_id, s.out_player_id, s.is_home) for s in target_list
        }
        substitution_key = (in_player.id, out_player.id, is_home)

        if substitution_key not in existing_substitutions:
            substitution_association = MatchSubstitutionAssociation(
                match=merged_match,
                in_player=in_player,
                out_player=out_player,
                clock=clock,
                is_home=is_home,
            )
            target_list.append(substitution_association)
        target_list.sort(key=lambda s: (s.is_home, s.clock))
        return merged_match
