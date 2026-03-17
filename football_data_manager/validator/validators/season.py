from __future__ import annotations

from collections import defaultdict
from datetime import timedelta

from sqlalchemy import select

from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.team_championship_association import (
    TeamChampionshipAssociation,
)
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class SeasonValidator(AbstractValidator):
    """Season entity validation."""

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="season")
        now = create_utc_now()

        async with self._session_factory.session() as session:
            season_ids = await self._resolve_scoped_season_ids(
                session=session,
                season_id=season_id,
                competition_id=competition_id,
            )

            stmt = select(SeasonEntity)
            if season_id or competition_id:
                if not season_ids:
                    result.add_warning(
                        "data_exists",
                        detail="No Season records matched the given scope",
                    )
                    return result
                stmt = stmt.where(SeasonEntity.id.in_(season_ids))

            seasons = (await session.execute(stmt)).scalars().all()
            if not seasons:
                result.add_warning("data_exists", detail="No Season records found")
                return result

            competition_ids = await self._load_id_set(session, CompetitionEntity)

            fixture_rows = (
                await session.execute(
                    select(
                        FixtureEntity.season_id,
                        FixtureEntity.home_team_id,
                        FixtureEntity.away_team_id,
                    )
                )
            ).all()
            fixture_count_by_season: dict[str, int] = defaultdict(int)
            fixture_team_ids_by_season: dict[str, set[str]] = defaultdict(set)
            for sid, home_team_id, away_team_id in fixture_rows:
                fixture_count_by_season[sid] += 1
                fixture_team_ids_by_season[sid].update({home_team_id, away_team_id})

            registration_rows = (
                await session.execute(
                    select(
                        TeamChampionshipAssociation.season_id,
                        TeamChampionshipAssociation.team_id,
                    )
                )
            ).all()
            registered_team_ids_by_season: dict[str, set[str]] = defaultdict(set)
            for sid, team_id_value in registration_rows:
                registered_team_ids_by_season[sid].add(team_id_value)

            for season in seasons:
                entity_id = season.id
                self.check_true(
                    result,
                    "date_start < date_end",
                    season.date_start < season.date_end,
                    entity_id,
                    detail=(
                        f"date_start={season.date_start}, date_end={season.date_end}"
                    ),
                )
                self.check_true(
                    result,
                    "year_start <= year_end",
                    season.year_start <= season.year_end,
                    entity_id,
                    detail=(
                        f"year_start={season.year_start}, year_end={season.year_end}"
                    ),
                )
                self.check_true(
                    result,
                    "year span <= 1",
                    (season.year_end - season.year_start) <= 1,
                    entity_id,
                    detail=(
                        f"year_start={season.year_start}, year_end={season.year_end}"
                    ),
                )
                self.check_not_empty(
                    result,
                    "abbreviation not empty",
                    season.abbreviation,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "competition_id FK",
                    season.competition_id,
                    competition_ids,
                    entity_id,
                )

                fixture_count = fixture_count_by_season.get(season.id, 0)
                if fixture_count > 0:
                    result.add_pass("has at least one fixture", entity_id)
                elif season.date_start > now:
                    result.add_skip("has at least one fixture", entity_id)
                else:
                    result.add_fail(
                        "has at least one fixture",
                        entity_id,
                        detail="No Fixture records found for season",
                    )

                registered_team_ids = registered_team_ids_by_season.get(season.id, set())
                if not registered_team_ids:
                    result.add_skip("registered team count reasonable", entity_id)
                elif 10 <= len(registered_team_ids) <= 30:
                    result.add_pass("registered team count reasonable", entity_id)
                else:
                    result.add_warning(
                        "registered team count reasonable",
                        entity_id,
                        detail=f"registered_teams={len(registered_team_ids)}",
                    )

                if not registered_team_ids:
                    result.add_skip(
                        "fixture team set matches registered teams",
                        entity_id,
                    )
                elif (
                    fixture_team_ids_by_season.get(season.id, set())
                    == registered_team_ids
                ):
                    result.add_pass("fixture team set matches registered teams", entity_id)
                else:
                    result.add_warning(
                        "fixture team set matches registered teams",
                        entity_id,
                        detail=(
                            f"fixture_teams={len(fixture_team_ids_by_season.get(season.id, set()))}, "
                            f"registered_teams={len(registered_team_ids)}"
                        ),
                    )

                low = season.date_start - timedelta(days=31)
                high = season.date_end + timedelta(days=31)
                out_of_range_exists = any(
                    sid == season.id and not (low <= kickoff <= high)
                    for sid, kickoff in (
                        await session.execute(
                            select(FixtureEntity.season_id, FixtureEntity.kickoff_time).where(
                                FixtureEntity.season_id == season.id
                            )
                        )
                    ).all()
                )
                self.check_true(
                    result,
                    "season fixtures within allowed range",
                    not out_of_range_exists,
                    entity_id,
                    detail="Found Fixture outside season date window",
                )

        return result
