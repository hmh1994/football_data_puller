from __future__ import annotations

from sqlalchemy import func, select

from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class CompetitionValidator(AbstractValidator):
    """Competition entity validation."""

    ALLOWED_SOURCE_IDS = {"1", "2", "5", "6", "8", "1007", "1125"}

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="competition")

        async with self._session_factory.session() as session:
            competition_ids = await self._resolve_scoped_competition_ids(
                session=session,
                competition_id=competition_id,
                season_id=season_id,
            )

            stmt = select(CompetitionEntity)
            if season_id or competition_id:
                if not competition_ids:
                    result.add_warning(
                        "data_exists",
                        detail="No Competition records matched the given scope",
                    )
                    return result
                stmt = stmt.where(CompetitionEntity.id.in_(competition_ids))

            competitions = (await session.execute(stmt)).scalars().all()
            if not competitions:
                result.add_warning("data_exists", detail="No Competition records found")
                return result

            season_counts = {
                competition_id_value: count
                for competition_id_value, count in (
                    await session.execute(
                        select(
                            SeasonEntity.competition_id,
                            func.count(SeasonEntity.id),
                        ).group_by(SeasonEntity.competition_id)
                    )
                ).all()
            }

            for competition in competitions:
                entity_id = competition.id
                self.check_not_empty(
                    result,
                    "name_en not empty",
                    competition.name_en,
                    entity_id,
                )
                self.check_not_empty(
                    result,
                    "abbreviation not empty",
                    competition.abbreviation,
                    entity_id,
                )
                self.check_true(
                    result,
                    "source_id allowed",
                    competition.source_id in self.ALLOWED_SOURCE_IDS,
                    entity_id,
                    detail=f"source_id={competition.source_id}",
                )
                self.check_true(
                    result,
                    "has at least one season",
                    season_counts.get(competition.id, 0) > 0,
                    entity_id,
                    detail="No Season records found for competition",
                )

        return result

