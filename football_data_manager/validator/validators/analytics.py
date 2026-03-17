from __future__ import annotations

from collections import defaultdict
from math import isfinite

from sqlalchemy import select

from football_data_manager.common.enums.analytics_key_enum import AnalyticsKeyEnum
from football_data_manager.repository.entities.analytics import AnalyticsEntity
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.match_stats import MatchStatEntity
from football_data_manager.repository.entities.match_substitution_association import (
    MatchSubstitutionAssociation,
)
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class AnalyticsValidator(AbstractValidator):
    """Analytics entity validation."""

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="analytics")

        async with self._session_factory.session() as session:
            season_ids = await self._resolve_scoped_season_ids(
                session=session,
                season_id=season_id,
                competition_id=competition_id,
            )

            stmt = select(AnalyticsEntity)
            if season_id or competition_id:
                if not season_ids:
                    result.add_warning(
                        "data_exists",
                        detail="No Analytics records matched the given scope",
                    )
                    return result
                stmt = stmt.where(AnalyticsEntity.season_id.in_(season_ids))

            analytics_rows = (await session.execute(stmt)).scalars().all()
            if not analytics_rows:
                result.add_warning("data_exists", detail="No Analytics records found")
                return result

            season_fk_ids = await self._load_id_set(session, SeasonEntity)
            seasons = {
                season_value.id: season_value
                for season_value in (
                    await session.execute(select(SeasonEntity))
                ).scalars()
            }

            matches_by_season: dict[str, list[MatchEntity]] = defaultdict(list)
            fixtures = {
                fixture_value.id: fixture_value
                for fixture_value in (
                    await session.execute(select(FixtureEntity))
                ).scalars()
            }
            matches = (
                await session.execute(select(MatchEntity))
            ).scalars().all()
            for match in matches:
                fixture_value = fixtures.get(match.fixture_id)
                if fixture_value is not None:
                    matches_by_season[fixture_value.season_id].append(match)

            match_stats_by_match: dict[str, list[MatchStatEntity]] = defaultdict(list)
            for match_stat in (
                await session.execute(select(MatchStatEntity))
            ).scalars().all():
                match_stats_by_match[match_stat.match_id].append(match_stat)

            substitutions_by_match: dict[str, int] = defaultdict(int)
            for match_id_value, in (
                await session.execute(select(MatchSubstitutionAssociation.match_id))
            ).all():
                substitutions_by_match[match_id_value] += 1

            derived_by_season: dict[str, dict[AnalyticsKeyEnum, float]] = {}
            previous_season_id: dict[str, str] = {}
            seasons_by_competition: dict[str, list[SeasonEntity]] = defaultdict(list)
            for season_value in seasons.values():
                seasons_by_competition[season_value.competition_id].append(season_value)
            for competition_seasons in seasons_by_competition.values():
                competition_seasons.sort(key=lambda item: item.date_end)
                for index, season_value in enumerate(competition_seasons):
                    if index > 0:
                        previous_season_id[season_value.id] = competition_seasons[index - 1].id

            for season_value in seasons.values():
                season_matches = matches_by_season.get(season_value.id, [])
                completed_matches = season_matches
                match_count = len(completed_matches)
                total_goals = sum(
                    match.home_team_score + match.away_team_score for match in completed_matches
                )
                total_yellow_cards = 0
                total_red_cards = 0
                total_xg = 0.0
                total_substitutions = 0
                pass_accuracy_values: list[float] = []

                for match in completed_matches:
                    stats = match_stats_by_match.get(match.id, [])
                    total_yellow_cards += sum(
                        stat.discipline_yellow_cards for stat in stats
                    )
                    total_red_cards += sum(stat.discipline_red_cards for stat in stats)
                    total_xg += sum(stat.expected_goals for stat in stats)
                    total_substitutions += substitutions_by_match.get(match.id, 0)
                    accurate = sum(stat.passes_accurate for stat in stats)
                    total_passes = sum(stat.passes_total for stat in stats)
                    if total_passes > 0:
                        pass_accuracy_values.append((accurate / total_passes) * 100.0)

                derived_by_season[season_value.id] = {
                    AnalyticsKeyEnum.PER_MATCH_GOALS: (
                        total_goals / match_count if match_count else 0.0
                    ),
                    AnalyticsKeyEnum.TOTAL_GOALS: float(total_goals),
                    AnalyticsKeyEnum.PER_MATCH_YELLOW_CARDS: (
                        total_yellow_cards / match_count if match_count else 0.0
                    ),
                    AnalyticsKeyEnum.TOTAL_RED_CARDS: float(total_red_cards),
                    AnalyticsKeyEnum.PER_MATCH_XG: total_xg / match_count if match_count else 0.0,
                    AnalyticsKeyEnum.PER_MATCH_SUBSTITUTIONS: (
                        total_substitutions / match_count if match_count else 0.0
                    ),
                    AnalyticsKeyEnum.PER_MATCH_PASS_ACCURACY: (
                        sum(pass_accuracy_values) / len(pass_accuracy_values)
                        if pass_accuracy_values
                        else 0.0
                    ),
                }

            for analytics in analytics_rows:
                entity_id = analytics.id
                self.check_true(
                    result,
                    "key valid",
                    isinstance(analytics.key, AnalyticsKeyEnum),
                    entity_id,
                    detail=f"key={analytics.key}",
                )
                self.check_true(
                    result,
                    "value finite",
                    isfinite(analytics.value),
                    entity_id,
                    detail=f"value={analytics.value}",
                )
                self.check_true(
                    result,
                    "delta finite or None",
                    analytics.delta is None or isfinite(analytics.delta),
                    entity_id,
                    detail=f"delta={analytics.delta}",
                )
                self.check_fk_exists(
                    result,
                    "season_id FK",
                    analytics.season_id,
                    season_fk_ids,
                    entity_id,
                )

                expected_value = derived_by_season.get(analytics.season_id, {}).get(
                    analytics.key
                )
                if expected_value is not None:
                    tolerance = 0.1
                    if analytics.key in {
                        AnalyticsKeyEnum.TOTAL_GOALS,
                        AnalyticsKeyEnum.TOTAL_RED_CARDS,
                    }:
                        tolerance = 0.0
                    self.check_equal(
                        result,
                        f"{analytics.key.value} derived value",
                        analytics.value,
                        expected_value,
                        entity_id,
                        tolerance=tolerance,
                    )

                prev_season_id = previous_season_id.get(analytics.season_id)
                if prev_season_id is None or analytics.delta is None:
                    continue
                prev_value = derived_by_season.get(prev_season_id, {}).get(analytics.key)
                if prev_value in (None, 0):
                    result.add_warning(
                        "delta derived value",
                        entity_id,
                        detail="Previous season value missing or zero",
                    )
                    continue
                expected_delta = ((analytics.value - prev_value) / prev_value) * 100.0
                self.check_equal(
                    result,
                    "delta derived value",
                    analytics.delta,
                    expected_delta,
                    entity_id,
                    tolerance=0.1,
                )

        return result

