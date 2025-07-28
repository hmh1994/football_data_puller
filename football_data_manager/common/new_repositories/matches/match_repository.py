from sqlalchemy.ext.asyncio import AsyncSession

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.matches.match_away_team_card_association import (
    MatchAwayTeamCardAssociation,
)
from football_data_manager.common.new_repositories.matches.match_away_team_goal_association import (
    MatchAwayTeamGoalAssociation,
)
from football_data_manager.common.new_repositories.matches.match_away_team_lineup_association import (
    MatchAwayTeamLineupAssociation,
)
from football_data_manager.common.new_repositories.matches.match_away_team_substitute_association import (
    MatchAwayTeamSubstituteAssociation,
)
from football_data_manager.common.new_repositories.matches.match_away_team_substitution_association import (
    MatchAwayTeamSubstitutionAssociation,
)
from football_data_manager.common.new_repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.new_repositories.matches.match_home_team_card_association import (
    MatchHomeTeamCardAssociation,
)
from football_data_manager.common.new_repositories.matches.match_home_team_goal_association import (
    MatchHomeTeamGoalAssociation,
)
from football_data_manager.common.new_repositories.matches.match_home_team_lineup_association import (
    MatchHomeTeamLineupAssociation,
)
from football_data_manager.common.new_repositories.matches.match_home_team_substitute_association import (
    MatchHomeTeamSubstituteAssociation,
)
from football_data_manager.common.new_repositories.matches.match_home_team_substitution_association import (
    MatchHomeTeamSubstitutionAssociation,
)
from football_data_manager.common.new_repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.new_repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.services.db.db_service import DbService


class MatchRepository(PulseliveRepository[MatchEntity]):
    """ """

    def __init__(self, db_service: DbService):
        super().__init__(db_service, MatchEntity)

    @BaseRepository.with_db_session
    async def load_items(self, session: AsyncSession, news: MatchEntity) -> MatchEntity:
        return await self._load_lazy_fields(
            session,
            news,
            [
                "away_team_cards",
                "away_team_goals",
                "away_team_lineup",
                "away_team_substitute",
                "away_team_substitution",
                "home_team_cards",
                "home_team_goals",
                "home_team_lineup",
                "home_team_substitute",
                "home_team_substitution",
            ],
        )

    async def append_card(
        self,
        match: MatchEntity,
        is_home: bool,
        player: PlayerEntity,
        card_type: CardTypeEnum,
        clock: int,
    ) -> MatchEntity:
        merged_match = await self.load_items(match)
        target_list = (
            merged_match.home_team_card_associations
            if is_home
            else merged_match.away_team_card_associations
        )
        card_id_list = [c.card_info for c in target_list]
        if (player.id, card_type, clock) not in card_id_list:
            params = {
                "player": player,
                "card_type": card_type,
                "clock": clock,
            }
            target_list.append(
                MatchHomeTeamCardAssociation(**params)
                if is_home
                else MatchAwayTeamCardAssociation(**params)
            )
        return merged_match

    async def append_goal(
        self,
        match: MatchEntity,
        is_home: bool,
        player: PlayerEntity,
        assist_player: PlayerEntity | None,
        is_penalty: bool,
        is_own_goal: bool,
        clock: int,
    ) -> MatchEntity:
        merged_match = await self.load_items(match)
        target_list = (
            merged_match.home_team_goal_associations
            if is_home
            else merged_match.away_team_goal_associations
        )
        goal_id_list = [(g.goal_info[0], g.goal_info[2]) for g in target_list]
        if (player.id, clock) not in goal_id_list:
            params = {
                "player": player,
                "assist_player": assist_player,
                "clock": clock,
                "is_penalty": is_penalty,
                "is_own_goal": is_own_goal,
            }
            target_list.append(
                MatchHomeTeamGoalAssociation(**params)
                if is_home
                else MatchAwayTeamGoalAssociation(**params)
            )
        return merged_match

    async def append_lineup(
        self,
        match: MatchEntity,
        is_home: bool,
        player: PlayerEntity,
        shirt_number: int,
        row: int,
        column: int,
    ) -> MatchEntity:
        merged_match = await self.load_items(match)
        target_list = (
            merged_match.home_team_lineup_associations
            if is_home
            else merged_match.away_team_lineup_associations
        )
        lineup_id_list = [l.player_info[0] for l in target_list]
        if player.id not in lineup_id_list:
            params = {
                "player": player,
                "shirt_number": shirt_number,
                "row": row,
                "column": column,
            }
            target_list.append(
                MatchHomeTeamLineupAssociation(**params)
                if is_home
                else MatchAwayTeamLineupAssociation(**params)
            )
        return merged_match

    async def append_substitute(
        self, match: MatchEntity, is_home: bool, player: PlayerEntity, shirt_number: int
    ) -> MatchEntity:
        merged_match = await self.load_items(match)
        target_list = (
            merged_match.home_team_substitute_associations
            if is_home
            else merged_match.away_team_substitute_associations
        )
        lineup_id_list = [l.player_info[0] for l in target_list]
        if player.id not in lineup_id_list:
            params = {
                "player": player,
                "shirt_number": shirt_number,
            }
            target_list.append(
                MatchHomeTeamSubstituteAssociation(**params)
                if is_home
                else MatchAwayTeamSubstituteAssociation(**params)
            )
        return merged_match

    async def append_substitution(
        self,
        match: MatchEntity,
        is_home: bool,
        in_player: PlayerEntity,
        out_player: PlayerEntity,
        clock: int,
    ) -> MatchEntity:
        merged_match = await self.load_items(match)
        target_list = (
            merged_match.home_team_substitution_associations
            if is_home
            else merged_match.away_team_substitution_associations
        )
        substitution_id_list = [s.substitution[0] for s in target_list]
        if (in_player.id, out_player.id) not in substitution_id_list:
            params = {
                "in_player": in_player,
                "out_player": out_player,
                "clock": clock,
            }
            target_list.append(
                MatchHomeTeamSubstitutionAssociation(**params)
                if is_home
                else MatchAwayTeamSubstitutionAssociation(**params)
            )
        return merged_match
