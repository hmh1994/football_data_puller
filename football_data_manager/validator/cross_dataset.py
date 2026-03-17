from __future__ import annotations

from collections import Counter, defaultdict

from sqlalchemy import func, select

from football_data_manager.repository.entities.analytics import AnalyticsEntity
from football_data_manager.repository.entities.awards import AwardEntity
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.entities.match_stats import MatchStatEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.news import NewsEntity
from football_data_manager.repository.entities.officials import OfficialEntity
from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.staffs import StaffEntity
from football_data_manager.repository.entities.team_championship_association import (
    TeamChampionshipAssociation,
)
from football_data_manager.repository.entities.team_stats import TeamStatEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class CrossDatasetValidator(AbstractValidator):
    """Cross-dataset validation across multiple entity types."""

    SOURCE_ID_MODELS = (
        AnalyticsEntity,
        AwardEntity,
        CompetitionEntity,
        FixtureEntity,
        GroundEntity,
        MatchEntity,
        MatchStatEntity,
        NewsEntity,
        OfficialEntity,
        PlayerEntity,
        PlayerStatEntity,
        SeasonEntity,
        StaffEntity,
        TeamEntity,
        TeamStatEntity,
    )

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="cross-dataset")

        async with self._session_factory.session() as session:
            season_ids = await self._resolve_scoped_season_ids(
                session=session,
                season_id=season_id,
                competition_id=competition_id,
            )

            team_stat_stmt = select(TeamStatEntity)
            fixture_stmt = select(FixtureEntity)
            team_assoc_stmt = select(
                TeamChampionshipAssociation.season_id,
                TeamChampionshipAssociation.team_id,
            )
            if season_id or competition_id:
                if not season_ids:
                    result.add_warning(
                        "data_exists",
                        detail="No records matched the given scope",
                    )
                    return result
                team_stat_stmt = team_stat_stmt.where(TeamStatEntity.season_id.in_(season_ids))
                fixture_stmt = fixture_stmt.where(FixtureEntity.season_id.in_(season_ids))
                team_assoc_stmt = team_assoc_stmt.where(
                    TeamChampionshipAssociation.season_id.in_(season_ids)
                )

            team_stats = (await session.execute(team_stat_stmt)).scalars().all()
            fixtures = (await session.execute(fixture_stmt)).scalars().all()
            registrations = (await session.execute(team_assoc_stmt)).all()

            stats_by_season: dict[str, list[TeamStatEntity]] = defaultdict(list)
            for team_stat in team_stats:
                stats_by_season[team_stat.season_id].append(team_stat)

            fixtures_by_season: dict[str, list[FixtureEntity]] = defaultdict(list)
            for fixture in fixtures:
                fixtures_by_season[fixture.season_id].append(fixture)

            team_ids_by_season: dict[str, set[str]] = defaultdict(set)
            for season_id_value, team_id_value in registrations:
                team_ids_by_season[season_id_value].add(team_id_value)

            for season_id_value, season_team_stats in stats_by_season.items():
                entity_id = season_id_value
                total_goals_for = sum(team_stat.overall_goals_for for team_stat in season_team_stats)
                total_goals_against = sum(
                    team_stat.overall_goals_against for team_stat in season_team_stats
                )
                total_wins = sum(team_stat.overall_matches_won for team_stat in season_team_stats)
                total_losses = sum(
                    team_stat.overall_matches_lost for team_stat in season_team_stats
                )
                total_draws = sum(
                    team_stat.overall_matches_drawn for team_stat in season_team_stats
                )
                total_matches = sum(team_stat.overall_matches for team_stat in season_team_stats)
                fixture_count = len(fixtures_by_season.get(season_id_value, []))
                team_count = len(team_ids_by_season.get(season_id_value, set()))

                self.check_equal(
                    result,
                    "sum(goals_for) == sum(goals_against)",
                    total_goals_for,
                    total_goals_against,
                    entity_id,
                )
                self.check_equal(
                    result,
                    "sum(matches_won) == sum(matches_lost)",
                    total_wins,
                    total_losses,
                    entity_id,
                )
                self.check_true(
                    result,
                    "sum(matches_drawn) is even",
                    total_draws % 2 == 0,
                    entity_id,
                    detail=f"sum_drawn={total_draws}",
                )
                if team_count == 0:
                    result.add_skip(
                        "sum(team_stat.matches) == fixture_count * 2",
                        entity_id,
                    )
                elif total_matches == fixture_count * 2:
                    result.add_pass(
                        "sum(team_stat.matches) == fixture_count * 2",
                        entity_id,
                    )
                else:
                    result.add_warning(
                        "sum(team_stat.matches) == fixture_count * 2",
                        entity_id,
                        detail=(
                            f"actual={total_matches}, expected={fixture_count * 2}"
                        ),
                    )

                if team_count == 0:
                    result.add_skip(
                        "fixture_count == team_count * (team_count - 1)",
                        entity_id,
                    )
                elif team_count == 1:
                    result.add_warning(
                        "fixture_count == team_count * (team_count - 1)",
                        entity_id,
                        detail=f"Insufficient team registration data (team_count={team_count})",
                    )
                else:
                    self.check_equal(
                        result,
                        "fixture_count == team_count * (team_count - 1)",
                        fixture_count,
                        team_count * (team_count - 1),
                        entity_id,
                    )

            for model in self.SOURCE_ID_MODELS:
                duplicate_rows = (
                    await session.execute(
                        select(model.source_id, func.count(model.id))
                        .group_by(model.source_id)
                        .having(func.count(model.id) > 1)
                    )
                ).all()
                if duplicate_rows:
                    result.add_fail(
                        f"{model.__name__} source_id unique",
                        detail=f"duplicates={duplicate_rows}",
                    )
                else:
                    result.add_pass(f"{model.__name__} source_id unique")

            match_counts = Counter(
                fixture_id_value
                for fixture_id_value, in (
                    await session.execute(select(MatchEntity.fixture_id))
                ).all()
            )
            missing_match_fixtures = [
                fixture.id
                for fixture in fixtures
                if match_counts.get(fixture.id, 0) == 0
            ]
            if missing_match_fixtures:
                result.add_warning(
                    "fixtures without matches within reasonable level",
                    detail=f"count={len(missing_match_fixtures)}",
                )
            else:
                result.add_pass("fixtures without matches within reasonable level")

            team_stat_keys = {(team_stat.season_id, team_stat.team_id) for team_stat in team_stats}
            missing_team_stats = [
                (season_id_value, team_id_value)
                for season_id_value, team_id_value in registrations
                if (season_id_value, team_id_value) not in team_stat_keys
            ]
            if missing_team_stats:
                result.add_warning(
                    "team-stat exists for registered team-season",
                    detail=f"missing={len(missing_team_stats)}",
                )
            else:
                result.add_pass("team-stat exists for registered team-season")

        return result
