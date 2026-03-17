from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select

from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.match_stats import MatchStatEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class MatchStatValidator(AbstractValidator):
    """MatchStat entity validation."""

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="match-stat")

        async with self._session_factory.session() as session:
            season_ids = await self._resolve_scoped_season_ids(
                session=session,
                season_id=season_id,
                competition_id=competition_id,
            )

            stmt = select(MatchStatEntity)
            if season_id or competition_id:
                if not season_ids:
                    result.add_warning(
                        "data_exists",
                        detail="No MatchStat records matched the given scope",
                    )
                    return result
                stmt = stmt.join(
                    MatchEntity,
                    MatchStatEntity.match_id == MatchEntity.id,
                ).join(
                    FixtureEntity,
                    MatchEntity.fixture_id == FixtureEntity.id,
                ).where(FixtureEntity.season_id.in_(season_ids))

            match_stats = (await session.execute(stmt)).scalars().all()
            if not match_stats:
                result.add_warning("data_exists", detail="No MatchStat records found")
                return result

            match_ids = await self._load_id_set(session, MatchEntity)
            team_ids = await self._load_id_set(session, TeamEntity)

            matches = {
                match_value.id: match_value
                for match_value in (
                    await session.execute(select(MatchEntity))
                ).scalars()
            }
            stats_by_match: dict[str, list[MatchStatEntity]] = defaultdict(list)
            for match_stat in match_stats:
                stats_by_match[match_stat.match_id].append(match_stat)

            for match_stat in match_stats:
                entity_id = match_stat.id

                self.check_equal(
                    result,
                    "shots_total == inside_box + outside_box",
                    match_stat.shots_total,
                    match_stat.shots_inside_box + match_stat.shots_outside_box,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "shots_on_target <= shots_total",
                    match_stat.shots_on_target,
                    match_stat.shots_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "shots_off_target <= shots_total",
                    match_stat.shots_off_target,
                    match_stat.shots_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "shots_blocked <= shots_total",
                    match_stat.shots_blocked,
                    match_stat.shots_total,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "duels_total == aerial_total + ground_total",
                    match_stat.duels_total,
                    match_stat.duels_aerial_total + match_stat.duels_ground_total,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "duels_won == aerial_won + ground_won",
                    match_stat.duels_won,
                    match_stat.duels_aerial_won + match_stat.duels_ground_won,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "duels_aerial_won <= duels_aerial_total",
                    match_stat.duels_aerial_won,
                    match_stat.duels_aerial_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "duels_ground_won <= duels_ground_total",
                    match_stat.duels_ground_won,
                    match_stat.duels_ground_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "duels_won <= duels_total",
                    match_stat.duels_won,
                    match_stat.duels_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "duels_dribbles_successful <= duels_dribbles_total",
                    match_stat.duels_dribbles_successful,
                    match_stat.duels_dribbles_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "passes_accurate <= passes_total",
                    match_stat.passes_accurate,
                    match_stat.passes_total,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "passes_accurate_crosses <= passes_total_crosses",
                    match_stat.passes_accurate_crosses,
                    match_stat.passes_total_crosses,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "passes_accurate_long_balls <= passes_total_long_balls",
                    match_stat.passes_accurate_long_balls,
                    match_stat.passes_total_long_balls,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "defense_tackles_won <= defense_tackles_total",
                    match_stat.defense_tackles_won,
                    match_stat.defense_tackles_total,
                    entity_id,
                )
                self.check_true(
                    result,
                    "big_chances >= big_chances_missed",
                    match_stat.big_chances >= match_stat.big_chances_missed,
                    entity_id,
                    detail=(
                        f"big_chances={match_stat.big_chances}, "
                        f"big_chances_missed={match_stat.big_chances_missed}"
                    ),
                )
                self.check_range(
                    result,
                    "possession in [0, 100]",
                    match_stat.possession,
                    0.0,
                    100.0,
                    entity_id,
                )
                self.check_non_negative(
                    result,
                    "expected_goals >= 0.0",
                    match_stat.expected_goals,
                    entity_id,
                )
                self.check_lte(
                    result,
                    "expected_goals_non_penalty <= expected_goals",
                    match_stat.expected_goals_non_penalty,
                    match_stat.expected_goals,
                    entity_id,
                )
                self.check_non_negative(
                    result,
                    "expected_goals_on_target >= 0.0",
                    match_stat.expected_goals_on_target,
                    entity_id,
                )
                for field_name in self.integer_field_names(MatchStatEntity):
                    self.check_non_negative(
                        result,
                        f"{field_name} >= 0",
                        getattr(match_stat, field_name),
                        entity_id,
                    )

                self.check_fk_exists(
                    result,
                    "match_id FK",
                    match_stat.match_id,
                    match_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "team_id FK",
                    match_stat.team_id,
                    team_ids,
                    entity_id,
                )

                match_value = matches.get(match_stat.match_id)
                if match_value is not None:
                    self.check_true(
                        result,
                        "team_id belongs to match teams",
                        match_stat.team_id
                        in {match_value.home_team_id, match_value.away_team_id},
                        entity_id,
                        detail=f"team_id={match_stat.team_id}",
                    )

            for match_id_value, related_stats in stats_by_match.items():
                match_value = matches.get(match_id_value)
                if match_value is None or match_value.period != PeriodEnum.FULLTIME:
                    continue
                if len(related_stats) == 2:
                    result.add_pass(
                        "exactly two MatchStat records for FULLTIME match",
                        match_id_value,
                    )
                    self.check_equal(
                        result,
                        "home + away possession ~= 100",
                        related_stats[0].possession + related_stats[1].possession,
                        100.0,
                        match_id_value,
                        tolerance=1.0,
                    )
                else:
                    result.add_fail(
                        "exactly two MatchStat records for FULLTIME match",
                        match_id_value,
                        detail=f"count={len(related_stats)}",
                    )

        return result
