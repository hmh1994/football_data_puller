from __future__ import annotations

import logging
from enum import StrEnum

from football_data_manager.validator.validators.base import (
    CheckLevel,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class ValidateEntity(StrEnum):
    """Supported validation targets."""

    COMPETITION = "competition"
    SEASON = "season"
    TEAM_STAT = "team-stat"
    PLAYER_STAT = "player-stat"
    MATCH = "match"
    MATCH_STAT = "match-stat"
    FIXTURE = "fixture"
    PLAYER = "player"
    ANALYTICS = "analytics"
    NEWS = "news"
    AWARD = "award"
    CROSS_DATASET = "cross-dataset"


VALIDATE_ORDER: list[ValidateEntity] = [
    ValidateEntity.COMPETITION,
    ValidateEntity.SEASON,
    ValidateEntity.PLAYER,
    ValidateEntity.FIXTURE,
    ValidateEntity.MATCH,
    ValidateEntity.MATCH_STAT,
    ValidateEntity.TEAM_STAT,
    ValidateEntity.PLAYER_STAT,
    ValidateEntity.ANALYTICS,
    ValidateEntity.NEWS,
    ValidateEntity.AWARD,
    ValidateEntity.CROSS_DATASET,
]


class ValidationOrchestrator:
    """Run one or many validators and collect results."""

    def __init__(self, container):
        self._container = container

    async def validate(
        self,
        target: ValidateEntity,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> list[ValidationResult]:
        validator = self._container.create_validator(target.value)
        result = await validator.validate(
            season_id=season_id,
            competition_id=competition_id,
        )
        return [result]

    async def validate_all(
        self,
        season_id: str | None = None,
        competition_id: str | None = None,
    ) -> list[ValidationResult]:
        results: list[ValidationResult] = []
        total = len(VALIDATE_ORDER)
        for index, entity in enumerate(VALIDATE_ORDER, 1):
            logger.info("[%d/%d] Validating %s ...", index, total, entity.value)
            try:
                validator = self._container.create_validator(entity.value)
                result = await validator.validate(
                    season_id=season_id,
                    competition_id=competition_id,
                )
            except Exception as error:
                logger.exception("Validation failed for %s", entity.value)
                result = ValidationResult(entity=entity.value)
                result.add_fail("validator_execution", detail=str(error))
            results.append(result)
            logger.info(
                "[%d/%d] Finished %s: PASS=%d, FAIL=%d, WARNING=%d, SKIP=%d",
                index,
                total,
                entity.value,
                result.pass_count,
                result.fail_count,
                result.warning_count,
                result.skip_count,
            )
        return results

    @staticmethod
    def print_summary(results: list[ValidationResult]) -> None:
        headers = ["Entity", "Total", "PASS", "FAIL", "WARNING", "SKIP", "Status"]
        widths = [15, 6, 6, 6, 8, 6, 8]

        def _line(values: list[str]) -> str:
            return " | ".join(
                value.ljust(width)
                for value, width in zip(values, widths, strict=False)
            )

        print(_line(headers))
        print("-" * (sum(widths) + 3 * (len(widths) - 1)))
        for result in results:
            print(
                _line(
                    [
                        result.entity,
                        str(result.total),
                        str(result.pass_count),
                        str(result.fail_count),
                        str(result.warning_count),
                        str(result.skip_count),
                        "OK" if result.success else "FAIL",
                    ]
                )
            )
        print("-" * (sum(widths) + 3 * (len(widths) - 1)))
        total_pass = sum(result.pass_count for result in results)
        total_fail = sum(result.fail_count for result in results)
        total_warning = sum(result.warning_count for result in results)
        total_skip = sum(result.skip_count for result in results)
        total_all = sum(result.total for result in results)
        print(
            _line(
                [
                    "Total",
                    str(total_all),
                    str(total_pass),
                    str(total_fail),
                    str(total_warning),
                    str(total_skip),
                    "OK" if all(result.success for result in results) else "FAIL",
                ]
            )
        )

    @staticmethod
    def print_detail(
        results: list[ValidationResult],
        level: CheckLevel | None = None,
    ) -> None:
        for result in results:
            filtered_checks = [
                check
                for check in result.checks
                if level is None or check.level == level
            ]
            if not filtered_checks:
                continue
            print(f"\n=== {result.entity} ===")
            for check in filtered_checks:
                entity_suffix = f" ({check.entity_id})" if check.entity_id else ""
                detail_suffix = f" - {check.detail}" if check.detail else ""
                print(
                    f"  [{check.level}] {check.rule}{entity_suffix}{detail_suffix}"
                )
