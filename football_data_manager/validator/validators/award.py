from __future__ import annotations

from sqlalchemy import select

from football_data_manager.common.enums.award_type_enum import AwardTypeEnum
from football_data_manager.repository.entities.awards import AwardEntity
from football_data_manager.repository.entities.player_stat_award_association import (
    PlayerStatAwardAssociation,
)
from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.entities.staff_award_association import (
    StaffAwardAssociation,
)
from football_data_manager.repository.entities.staffs import StaffEntity
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class AwardValidator(AbstractValidator):
    """Award entity validation."""

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        _ = season_id, competition_id
        result = ValidationResult(entity="award")

        async with self._session_factory.session() as session:
            awards = (await session.execute(select(AwardEntity))).scalars().all()
            if not awards:
                result.add_warning("data_exists", detail="No Award records found")
                return result

            player_stat_ids = await self._load_id_set(session, PlayerStatEntity)
            staff_ids = await self._load_id_set(session, StaffEntity)

            player_award_rows = (
                await session.execute(select(PlayerStatAwardAssociation))
            ).scalars().all()
            staff_award_rows = (
                await session.execute(select(StaffAwardAssociation))
            ).scalars().all()

            for award in awards:
                entity_id = award.id
                self.check_true(
                    result,
                    "type valid",
                    isinstance(award.type, AwardTypeEnum),
                    entity_id,
                    detail=f"type={award.type}",
                )

                for association in player_award_rows:
                    if association.award_id != award.id:
                        continue
                    self.check_fk_exists(
                        result,
                        "PlayerStatAwardAssociation player_stat_id FK",
                        association.player_stat_id,
                        player_stat_ids,
                        entity_id,
                    )
                    self.check_true(
                        result,
                        "PlayerStatAwardAssociation date valid",
                        association.date is not None,
                        entity_id,
                    )

                for association in staff_award_rows:
                    if association.award_id != award.id:
                        continue
                    self.check_fk_exists(
                        result,
                        "StaffAwardAssociation staff_id FK",
                        association.staff_id,
                        staff_ids,
                        entity_id,
                    )
                    self.check_true(
                        result,
                        "StaffAwardAssociation date valid",
                        association.date is not None,
                        entity_id,
                    )

        return result
