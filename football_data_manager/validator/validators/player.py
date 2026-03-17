from __future__ import annotations

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.enums.side_enum import SideEnum
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_now,
)
from football_data_manager.repository.entities.player_championship_association import (
    PlayerChampionshipAssociation,
)
from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    ValidationResult,
)


class PlayerValidator(AbstractValidator):
    """Player entity validation."""

    async def validate(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> ValidationResult:
        result = ValidationResult(entity="player")
        now = create_utc_now()

        async with self._session_factory.session() as session:
            season_ids = await self._resolve_scoped_season_ids(
                session=session,
                season_id=season_id,
                competition_id=competition_id,
            )

            stmt = select(PlayerEntity).options(
                selectinload(PlayerEntity.championship_season_associations)
            )
            if season_id or competition_id:
                player_ids = {
                    row[0]
                    for row in (
                        await session.execute(
                            select(PlayerChampionshipAssociation.player_id).where(
                                PlayerChampionshipAssociation.season_id.in_(season_ids)
                            )
                        )
                    ).all()
                }
                if not player_ids:
                    result.add_warning(
                        "data_exists",
                        detail="No Player records matched the given scope",
                    )
                    return result
                stmt = stmt.where(PlayerEntity.id.in_(player_ids))

            players = (await session.execute(stmt)).scalars().all()
            if not players:
                result.add_warning("data_exists", detail="No Player records found")
                return result

            any_pca_exists = bool(
                (
                    await session.execute(
                        select(PlayerChampionshipAssociation.player_id).limit(1)
                    )
                ).first()
            )

            player_stat_rows = (
                await session.execute(
                    select(PlayerStatEntity.player_id, PlayerStatEntity.season_id)
                )
            ).all()
            player_stat_seasons: dict[str, set[str]] = defaultdict(set)
            for player_id_value, player_season_id in player_stat_rows:
                player_stat_seasons[player_id_value].add(player_season_id)

            for player in players:
                entity_id = player.id
                self.check_not_empty(
                    result,
                    "display_name_en not empty",
                    player.display_name_en,
                    entity_id,
                )
                self.check_not_empty(
                    result,
                    "full_name not empty",
                    player.full_name,
                    entity_id,
                )
                self.check_true(
                    result,
                    "position valid",
                    isinstance(player.position, PositionEnum),
                    entity_id,
                    detail=f"position={player.position}",
                )
                self.check_true(
                    result,
                    "preferred_foot valid",
                    isinstance(player.preferred_foot, SideEnum),
                    entity_id,
                    detail=f"preferred_foot={player.preferred_foot}",
                )
                self.check_positive(result, "height > 0", player.height, entity_id)
                self.check_positive(result, "weight > 0", player.weight, entity_id)
                if player.birth_date is not None:
                    self.check_true(
                        result,
                        "birth_date < now",
                        player.birth_date < now,
                        entity_id,
                        detail=f"birth_date={player.birth_date}",
                    )

                associations = list(player.championship_season_associations)
                relevant_associations = [
                    association
                    for association in associations
                    if not season_ids or association.season_id in season_ids
                ]
                if not any_pca_exists:
                    result.add_skip("has PlayerChampionshipAssociation", entity_id)
                elif relevant_associations:
                    result.add_pass(
                        "has PlayerChampionshipAssociation",
                        entity_id,
                    )
                elif associations and (season_id or competition_id):
                    result.add_warning(
                        "has PlayerChampionshipAssociation",
                        entity_id,
                        detail="Player exists but not in scoped seasons",
                    )
                else:
                    result.add_fail(
                        "has PlayerChampionshipAssociation",
                        entity_id,
                        detail="No PlayerChampionshipAssociation found",
                    )

                for association in relevant_associations:
                    if association.season_id in player_stat_seasons.get(player.id, set()):
                        result.add_pass(
                            "PlayerStat exists for associated season",
                            entity_id,
                            detail=f"season_id={association.season_id}",
                        )

        return result
