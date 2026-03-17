from football_data_manager.validator.cross_dataset import CrossDatasetValidator
from football_data_manager.validator.container import ValidatorContainer
from football_data_manager.validator.validators.analytics import AnalyticsValidator
from football_data_manager.validator.validators.award import AwardValidator
from football_data_manager.validator.validators.competition import CompetitionValidator
from football_data_manager.validator.validators.fixture import FixtureValidator
from football_data_manager.validator.validators.match import MatchValidator
from football_data_manager.validator.validators.match_stat import MatchStatValidator
from football_data_manager.validator.validators.news import NewsValidator
from football_data_manager.validator.validators.player import PlayerValidator
from football_data_manager.validator.validators.player_stat import PlayerStatValidator
from football_data_manager.validator.validators.season import SeasonValidator
from football_data_manager.validator.validators.team_stat import TeamStatValidator


def test_validator_container_smoke() -> None:
    container = ValidatorContainer(session_factory=object())  # type: ignore[arg-type]

    assert isinstance(container.create_validator("competition"), CompetitionValidator)
    assert isinstance(container.create_validator("season"), SeasonValidator)
    assert isinstance(container.create_validator("player"), PlayerValidator)
    assert isinstance(container.create_validator("fixture"), FixtureValidator)
    assert isinstance(container.create_validator("match"), MatchValidator)
    assert isinstance(container.create_validator("match-stat"), MatchStatValidator)
    assert isinstance(container.create_validator("team-stat"), TeamStatValidator)
    assert isinstance(container.create_validator("player-stat"), PlayerStatValidator)
    assert isinstance(container.create_validator("analytics"), AnalyticsValidator)
    assert isinstance(container.create_validator("news"), NewsValidator)
    assert isinstance(container.create_validator("award"), AwardValidator)
    assert isinstance(
        container.create_validator("cross-dataset"),
        CrossDatasetValidator,
    )
