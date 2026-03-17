from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from football_data_manager.common.enums.card_type_enum import CardTypeEnum
from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.match_card_association import (
    MatchCardAssociation,
)
from football_data_manager.repository.entities.match_goal_association import (
    MatchGoalAssociation,
)
from football_data_manager.repository.entities.match_lineup_association import (
    MatchLineupAssociation,
)
from football_data_manager.repository.entities.match_substitute_association import (
    MatchSubstituteAssociation,
)
from football_data_manager.repository.entities.match_substitution_association import (
    MatchSubstitutionAssociation,
)
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.officials import OfficialEntity
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.staffs import StaffEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class MatchValidator(AbstractValidator):
    """Match entity validation."""

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="match")
        now = create_utc_now()

        async with self._session_factory.session() as session:
            season_ids = await self._resolve_scoped_season_ids(
                session=session,
                season_id=season_id,
                competition_id=competition_id,
            )

            stmt = select(MatchEntity).options(
                selectinload(MatchEntity.lineup_associations),
                selectinload(MatchEntity.goal_associations),
                selectinload(MatchEntity.card_associations),
                selectinload(MatchEntity.substitute_associations),
                selectinload(MatchEntity.substitution_associations),
            )
            if season_id or competition_id:
                if not season_ids:
                    result.add_warning(
                        "data_exists",
                        detail="No Match records matched the given scope",
                    )
                    return result
                stmt = stmt.join(
                    FixtureEntity,
                    MatchEntity.fixture_id == FixtureEntity.id,
                ).where(FixtureEntity.season_id.in_(season_ids))

            matches = (await session.execute(stmt)).scalars().all()
            if not matches:
                result.add_warning("data_exists", detail="No Match records found")
                return result

            team_ids = await self._load_id_set(session, TeamEntity)
            player_ids = await self._load_id_set(session, PlayerEntity)
            staff_ids = await self._load_id_set(session, StaffEntity)
            official_ids = await self._load_id_set(session, OfficialEntity)
            fixture_ids = await self._load_id_set(session, FixtureEntity)

            fixture_map = {
                fixture_value.id: fixture_value
                for fixture_value in (
                    await session.execute(select(FixtureEntity))
                ).scalars()
            }

            for match in matches:
                entity_id = match.id
                self.check_non_negative(
                    result,
                    "home_team_score >= 0",
                    match.home_team_score,
                    entity_id,
                )
                self.check_non_negative(
                    result,
                    "away_team_score >= 0",
                    match.away_team_score,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "home_team_half_time_score <= home_team_score",
                    match.home_team_half_time_score,
                    match.home_team_score,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "away_team_half_time_score <= away_team_score",
                    match.away_team_half_time_score,
                    match.away_team_score,
                    entity_id,
                )
                self.check_non_negative(result, "clock >= 0", match.clock, entity_id)
                self.check_true(
                    result,
                    "home_team_id != away_team_id",
                    match.home_team_id != match.away_team_id,
                    entity_id,
                    detail="Match has same home and away team",
                )
                self.check_non_negative(
                    result,
                    "attendance >= 0",
                    match.attendance,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "fixture_id FK",
                    match.fixture_id,
                    fixture_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "home_team_id FK",
                    match.home_team_id,
                    team_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "away_team_id FK",
                    match.away_team_id,
                    team_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "home_team_captain_id FK",
                    match.home_team_captain_id,
                    player_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "away_team_captain_id FK",
                    match.away_team_captain_id,
                    player_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "home_team_manager FK",
                    match.home_team_manager,
                    staff_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "away_team_manager FK",
                    match.away_team_manager,
                    staff_ids,
                    entity_id,
                )
                for rule, official_id in {
                    "official_main_referee_id FK": match.official_main_referee_id,
                    "official_assistant_1_referee_id FK": (
                        match.official_assistant_1_referee_id
                    ),
                    "official_assistant_2_referee_id FK": (
                        match.official_assistant_2_referee_id
                    ),
                    "official_fourth_referee_id FK": match.official_fourth_referee_id,
                    "official_var_id FK": match.official_var_id,
                    "official_assistant_var_id FK": match.official_assistant_var_id,
                }.items():
                    self.check_fk_exists(
                        result,
                        rule,
                        official_id,
                        official_ids,
                        entity_id,
                    )

                fixture_value = fixture_map.get(match.fixture_id)
                match_progressed = (
                    fixture_value is not None
                    and fixture_value.kickoff_time is not None
                    and fixture_value.kickoff_time + timedelta(minutes=match.clock) < now
                )
                if match_progressed:
                    self.check_equal(
                        result,
                        "home_team_formation sum == 10",
                        sum(match.home_team_formation or []),
                        10,
                        entity_id,
                    )
                    self.check_equal(
                        result,
                        "away_team_formation sum == 10",
                        sum(match.away_team_formation or []),
                        10,
                        entity_id,
                    )
                if fixture_value is not None:
                    self.check_true(
                        result,
                        "Match.home_team_id == Fixture.home_team_id",
                        match.home_team_id == fixture_value.home_team_id,
                        entity_id,
                        detail=f"fixture_id={match.fixture_id}",
                    )
                    self.check_true(
                        result,
                        "Match.away_team_id == Fixture.away_team_id",
                        match.away_team_id == fixture_value.away_team_id,
                        entity_id,
                        detail=f"fixture_id={match.fixture_id}",
                    )

                if match.period == PeriodEnum.FULLTIME:
                    self._check_lineups(result, match)
                    self._check_goals(result, match)
                    self._check_cards(result, match)
                    self._check_substitutions(result, match)

        return result

    def _check_lineups(self, result: ValidationResult, match: MatchEntity) -> None:
        entity_id = match.id
        home_lineup = [entry for entry in list(match.lineup_associations) if entry.is_home]
        away_lineup = [entry for entry in list(match.lineup_associations) if not entry.is_home]
        self.check_equal(result, "home lineup size == 11", len(home_lineup), 11, entity_id)
        self.check_equal(result, "away lineup size == 11", len(away_lineup), 11, entity_id)

        for side_label, lineup in {"home": home_lineup, "away": away_lineup}.items():
            shirt_numbers = [entry.shirt_number for entry in lineup]
            self.check_true(
                result,
                f"{side_label} lineup shirt numbers unique",
                len(shirt_numbers) == len(set(shirt_numbers)),
                entity_id,
                detail=f"{side_label}_shirt_numbers={shirt_numbers}",
            )
            for entry in lineup:
                self.check_true(
                    result,
                    "lineup position valid",
                    isinstance(entry.position, PositionEnum),
                    entity_id,
                    detail=f"player_id={entry.player_id}",
                )

    def _check_goals(self, result: ValidationResult, match: MatchEntity) -> None:
        entity_id = match.id
        home_players = {
            entry.player_id
            for entry in list(match.lineup_associations) + list(match.substitute_associations)
            if entry.is_home
        }
        away_players = {
            entry.player_id
            for entry in list(match.lineup_associations) + list(match.substitute_associations)
            if not entry.is_home
        }

        home_goal_count = 0
        away_goal_count = 0
        for goal in list(match.goal_associations):
            if goal.is_home and not goal.is_own_goal:
                home_goal_count += 1
            elif goal.is_home and goal.is_own_goal:
                away_goal_count += 1
            elif not goal.is_home and goal.is_own_goal:
                home_goal_count += 1
            else:
                away_goal_count += 1

            valid_players = home_players if goal.is_home else away_players
            self.check_true(
                result,
                "goal scorer belongs to lineup or bench",
                goal.player_id in valid_players,
                entity_id,
                detail=f"player_id={goal.player_id}",
            )
            self.check_range(
                result,
                "goal clock within match range",
                goal.clock,
                0,
                match.clock,
                entity_id,
            )

        self.check_equal(
            result,
            "home goals from associations == home_team_score",
            home_goal_count,
            match.home_team_score,
            entity_id,
        )
        self.check_equal(
            result,
            "away goals from associations == away_team_score",
            away_goal_count,
            match.away_team_score,
            entity_id,
        )

    def _check_cards(self, result: ValidationResult, match: MatchEntity) -> None:
        entity_id = match.id
        home_players = {
            entry.player_id
            for entry in list(match.lineup_associations) + list(match.substitute_associations)
            if entry.is_home
        }
        away_players = {
            entry.player_id
            for entry in list(match.lineup_associations) + list(match.substitute_associations)
            if not entry.is_home
        }
        for card in list(match.card_associations):
            valid_players = home_players if card.is_home else away_players
            self.check_true(
                result,
                "carded player belongs to lineup or bench",
                card.player_id in valid_players,
                entity_id,
                detail=f"player_id={card.player_id}",
            )
            self.check_range(
                result,
                "card clock within match range",
                card.clock,
                0,
                match.clock,
                entity_id,
            )
            self.check_true(
                result,
                "card_type valid",
                isinstance(card.card_type, CardTypeEnum),
                entity_id,
                detail=f"card_type={card.card_type}",
            )

    def _check_substitutions(self, result: ValidationResult, match: MatchEntity) -> None:
        entity_id = match.id
        home_lineup = {
            entry.player_id for entry in list(match.lineup_associations) if entry.is_home
        }
        away_lineup = {
            entry.player_id for entry in list(match.lineup_associations) if not entry.is_home
        }
        home_bench = {
            entry.player_id for entry in list(match.substitute_associations) if entry.is_home
        }
        away_bench = {
            entry.player_id
            for entry in list(match.substitute_associations)
            if not entry.is_home
        }

        grouped: dict[bool, list[MatchSubstitutionAssociation]] = defaultdict(list)
        for substitution in list(match.substitution_associations):
            grouped[substitution.is_home].append(substitution)
            self.check_range(
                result,
                "substitution clock within match range",
                substitution.clock,
                0,
                match.clock,
                entity_id,
            )

        for is_home, substitutions in grouped.items():
            side_label = "home" if is_home else "away"
            self.check_true(
                result,
                f"{side_label} substitutions <= 6",
                len(substitutions) <= 6,
                entity_id,
                detail=f"count={len(substitutions)}",
            )
            clocks = [entry.clock for entry in substitutions]
            self.check_true(
                result,
                f"{side_label} substitutions sorted",
                clocks == sorted(clocks),
                entity_id,
                detail=f"clocks={clocks}",
            )

            valid_in_players = home_bench if is_home else away_bench
            valid_out_players = set(home_lineup if is_home else away_lineup)
            for substitution in substitutions:
                self.check_true(
                    result,
                    "in_player belongs to bench",
                    substitution.in_player_id in valid_in_players,
                    entity_id,
                    detail=f"in_player_id={substitution.in_player_id}",
                )
                self.check_true(
                    result,
                    "out_player belongs to lineup or previous in_player",
                    substitution.out_player_id in valid_out_players,
                    entity_id,
                    detail=f"out_player_id={substitution.out_player_id}",
                )
                valid_out_players.add(substitution.in_player_id)
