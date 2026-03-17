from types import SimpleNamespace

from football_data_manager.repository.entities.team_stats import TeamStatEntity
from football_data_manager.validator.validators.match import MatchValidator
from football_data_manager.validator.validators.team_stat import TeamStatValidator
from football_data_manager.validator.validators.base import (
    AbstractValidator,
    CheckLevel,
    ValidationResult,
)


def test_validation_result_counts() -> None:
    result = ValidationResult(entity="test")
    result.add_pass("rule_1")
    result.add_pass("rule_2")
    result.add_fail("rule_3", detail="mismatch")
    result.add_warning("rule_4")
    result.add_skip("rule_5")

    assert result.pass_count == 2
    assert result.fail_count == 1
    assert result.warning_count == 1
    assert result.skip_count == 1
    assert result.total == 5
    assert result.success is False


def test_validation_result_success_with_warning_and_skip_only() -> None:
    result = ValidationResult(entity="test")
    result.add_pass("rule_1")
    result.add_warning("rule_2")
    result.add_skip("rule_3")

    assert result.success is True


def test_check_equal_pass() -> None:
    result = ValidationResult(entity="test")

    AbstractValidator.check_equal(result, "test_rule", 10, 10)

    assert result.pass_count == 1
    assert result.checks[0].level == CheckLevel.PASS


def test_check_equal_fail() -> None:
    result = ValidationResult(entity="test")

    AbstractValidator.check_equal(result, "test_rule", 10, 11)

    assert result.fail_count == 1
    assert "expected=11" in result.checks[0].detail


def test_team_stat_validator_allows_negative_goal_difference() -> None:
    validator = TeamStatValidator(session_factory=object())  # type: ignore[arg-type]
    result = ValidationResult(entity="team-stat")

    values = {field_name: 0 for field_name in validator.integer_field_names(TeamStatEntity)}
    values.update(
        {
            "id": "ts-1",
            "overall_goals_difference": -10,
            "home_goals_difference": -4,
            "away_goals_difference": -6,
            "overall_stat_average_possession": 50.0,
            "overall_stat_attack_expected_goals": 0.0,
            "overall_stat_attack_expected_assists": 0.0,
        }
    )
    team_stat = SimpleNamespace(**values)

    validator._check_stat_fields(result, team_stat)

    assert not any(
        check.rule.endswith("goals_difference >= 0") for check in result.checks
    )
    assert result.fail_count == 0


def test_match_validator_allows_six_substitutions() -> None:
    validator = MatchValidator(session_factory=object())  # type: ignore[arg-type]
    result = ValidationResult(entity="match")
    lineup = [
        SimpleNamespace(player_id=f"home-lineup-{index}", is_home=True)
        for index in range(11)
    ]
    bench = [
        SimpleNamespace(player_id=f"home-bench-{index}", is_home=True)
        for index in range(6)
    ]
    substitutions = [
        SimpleNamespace(
            in_player_id=f"home-bench-{index}",
            out_player_id=f"home-lineup-{index}",
            clock=60 + index,
            is_home=True,
        )
        for index in range(6)
    ]
    match = SimpleNamespace(
        id="match-1",
        clock=120,
        lineup_associations=lineup,
        substitute_associations=bench,
        substitution_associations=substitutions,
    )

    validator._check_substitutions(result, match)

    assert any(
        check.rule == "home substitutions <= 6" and check.level == CheckLevel.PASS
        for check in result.checks
    )
    assert not any(
        check.rule == "home substitutions <= 6" and check.level == CheckLevel.FAIL
        for check in result.checks
    )
