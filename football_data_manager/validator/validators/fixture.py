from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta

from sqlalchemy import select

from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.team_championship_association import (
    TeamChampionshipAssociation,
)
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class FixtureValidator(AbstractValidator):
    """Fixture entity validation."""

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="fixture")
        now = create_utc_now()

        async with self._session_factory.session() as session:
            season_ids = await self._resolve_scoped_season_ids(
                session=session,
                season_id=season_id,
                competition_id=competition_id,
            )

            stmt = select(FixtureEntity)
            if season_id or competition_id:
                if not season_ids:
                    result.add_warning(
                        "data_exists",
                        detail="No Fixture records matched the given scope",
                    )
                    return result
                stmt = stmt.where(FixtureEntity.season_id.in_(season_ids))

            fixtures = (await session.execute(stmt)).scalars().all()
            if not fixtures:
                result.add_warning("data_exists", detail="No Fixture records found")
                return result

            team_ids = await self._load_id_set(session, TeamEntity)
            season_fk_ids = await self._load_id_set(session, SeasonEntity)
            ground_ids = await self._load_id_set(session, GroundEntity)
            seasons = {
                season_value.id: season_value
                for season_value in (
                    await session.execute(select(SeasonEntity))
                ).scalars()
            }

            registrations: dict[str, set[str]] = defaultdict(set)
            for sid, team_id_value in (
                await session.execute(
                    select(
                        TeamChampionshipAssociation.season_id,
                        TeamChampionshipAssociation.team_id,
                    )
                )
            ).all():
                registrations[sid].add(team_id_value)

            match_counts = Counter(
                fixture_id_value
                for fixture_id_value, in (
                    await session.execute(select(MatchEntity.fixture_id))
                ).all()
            )

            duplicate_counts = Counter(
                (fixture.season_id, fixture.home_team_id, fixture.away_team_id, fixture.game_week)
                for fixture in fixtures
            )

            for fixture in fixtures:
                entity_id = fixture.id
                self.check_true(
                    result,
                    "home_team_id != away_team_id",
                    fixture.home_team_id != fixture.away_team_id,
                    entity_id,
                    detail="Fixture has same home and away team",
                )
                self.check_true(
                    result,
                    "game_week >= 1",
                    fixture.game_week >= 1,
                    entity_id,
                    detail=f"game_week={fixture.game_week}",
                )
                self.check_true(
                    result,
                    "kickoff_time valid",
                    fixture.kickoff_time is not None,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "home_team_id FK",
                    fixture.home_team_id,
                    team_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "away_team_id FK",
                    fixture.away_team_id,
                    team_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "season_id FK",
                    fixture.season_id,
                    season_fk_ids,
                    entity_id,
                )
                self.check_fk_exists(
                    result,
                    "ground_id FK",
                    fixture.ground_id,
                    ground_ids,
                    entity_id,
                )

                season_value = seasons.get(fixture.season_id)
                if season_value is not None:
                    low = season_value.date_start - timedelta(days=31)
                    high = season_value.date_end + timedelta(days=31)
                    self.check_true(
                        result,
                        "kickoff_time within season range",
                        low <= fixture.kickoff_time <= high,
                        entity_id,
                        detail=(
                            f"kickoff_time={fixture.kickoff_time}, "
                            f"allowed=[{low}, {high}]"
                        ),
                    )

                combo = (
                    fixture.season_id,
                    fixture.home_team_id,
                    fixture.away_team_id,
                    fixture.game_week,
                )
                self.check_true(
                    result,
                    "home+away+game_week unique within season",
                    duplicate_counts[combo] == 1,
                    entity_id,
                    detail=f"duplicate_count={duplicate_counts[combo]}",
                )

                season_team_ids = registrations.get(fixture.season_id, set())
                if not season_team_ids:
                    result.add_skip("home team registered for season", entity_id)
                    result.add_skip("away team registered for season", entity_id)
                else:
                    self.check_true(
                        result,
                        "home team registered for season",
                        fixture.home_team_id in season_team_ids,
                        entity_id,
                        detail=f"season_id={fixture.season_id}",
                    )
                    self.check_true(
                        result,
                        "away team registered for season",
                        fixture.away_team_id in season_team_ids,
                        entity_id,
                        detail=f"season_id={fixture.season_id}",
                    )

                match_count = match_counts.get(fixture.id, 0)
                if match_count == 1:
                    result.add_pass("exactly one match per fixture", entity_id)
                elif match_count == 0 and fixture.kickoff_time > now:
                    result.add_warning(
                        "exactly one match per fixture",
                        entity_id,
                        detail="No Match record yet for future fixture",
                    )
                else:
                    result.add_fail(
                        "exactly one match per fixture",
                        entity_id,
                        detail=f"match_count={match_count}",
                    )

        return result
