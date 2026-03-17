from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.match_card_association import MatchCardAssociation
from football_data_manager.repository.entities.match_goal_association import MatchGoalAssociation
from football_data_manager.repository.entities.match_lineup_association import MatchLineupAssociation
from football_data_manager.repository.entities.match_substitute_association import MatchSubstituteAssociation
from football_data_manager.repository.entities.match_substitution_association import MatchSubstitutionAssociation
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class MatchRepository(PulseliveRepository[MatchEntity]):
    """Repository for match entities with association management."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, MatchEntity)

    async def load_items(self, match: MatchEntity) -> MatchEntity:
        """
        Load all match association items (lazy-loaded relationships).

        :param match: Match entity
        :return: Match with all associations loaded
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

    async def get_by_fixture(
        self, fixture: FixtureEntity
    ) -> MatchEntity | None:
        """
        Get match by fixture.

        :param fixture: Fixture entity
        :return: Match entity or None
        """
        return await self._get_one_by_field(fixture_id=fixture.id)

    async def get_by_team_on_season(
        self,
        season: SeasonEntity,
        team: TeamEntity,
        session: AsyncSession | None = None,
    ) -> list[MatchEntity]:
        """
        Get matches for a specific team in a given season.

        :param season: Season entity
        :param team: Team entity
        :param session: Optional existing session
        :return: List of match entities ordered by game week
        """
        async def _do(s: AsyncSession) -> list[MatchEntity]:
            stmt = (
                select(MatchEntity)
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
            result = await s.execute(stmt)
            return list(result.scalars().all())

        if session:
            return await _do(session)
        return await self._execute_with_retry(_do)

    async def get_by_season(
        self,
        season: SeasonEntity,
        session: AsyncSession | None = None,
    ) -> list[MatchEntity]:
        """
        Get all matches for a given season.

        :param season: Season entity
        :param session: Optional existing session
        :return: List of match entities ordered by game week
        """
        async def _do(s: AsyncSession) -> list[MatchEntity]:
            stmt = (
                select(MatchEntity)
                .join(FixtureEntity, MatchEntity.fixture_id == FixtureEntity.id)
                .where(FixtureEntity.season_id == season.id)
                .order_by(FixtureEntity.game_week)
            )
            result = await s.execute(stmt)
            return list(result.scalars().all())

        if session:
            return await _do(session)
        return await self._execute_with_retry(_do)

    async def append_card(
        self,
        match: MatchEntity,
        is_home: bool,
        player: PlayerEntity,
        index: int,
        card_type: CardTypeEnum,
        clock: int,
    ) -> MatchEntity:
        """
        Append a card to the match if it doesn't already exist.

        :param match: Match entity
        :param is_home: Whether this is for the home team
        :param player: Player who received the card
        :param index: Card index
        :param card_type: Type of card
        :param clock: Match clock time
        :return: Updated match entity
        """
        merged_match = await self.load_items(match)
        target_list = merged_match.card_associations

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

        :param match: Match entity
        :param is_home: Whether scored by home team
        :param player: Goal scorer
        :param assist_player: Assist provider or None
        :param index: Goal index
        :param is_penalty: Whether from penalty
        :param is_own_goal: Whether own goal
        :param clock: Match clock time
        :return: Updated match entity
        """
        merged_match = await self.load_items(match)
        target_list = merged_match.goal_associations

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

        :param match: Match entity
        :param is_home: Whether home team lineup
        :param player: Player entity
        :param position: Player position
        :param shirt_number: Jersey number
        :param row: Formation row
        :param column: Formation column
        :return: Updated match entity
        """
        merged_match = await self.load_items(match)
        target_list = merged_match.lineup_associations

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

        :param match: Match entity
        :param is_home: Whether home team substitute
        :param player: Substitute player entity
        :param position: Player position
        :param shirt_number: Jersey number
        :return: Updated match entity
        """
        merged_match = await self.load_items(match)
        target_list = merged_match.substitute_associations

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

        :param match: Match entity
        :param is_home: Whether home team substitution
        :param in_player: Player coming on
        :param out_player: Player going off
        :param clock: Match clock time
        :return: Updated match entity
        """
        merged_match = await self.load_items(match)
        target_list = merged_match.substitution_associations

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
