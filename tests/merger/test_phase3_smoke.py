from pathlib import Path

from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.enums.side_enum import SideEnum
from football_data_manager.common.services.config.config_service import ConfigService
from football_data_manager.merger.container import MergerContainer
from football_data_manager.merger.mergers.award import AwardMerger
from football_data_manager.merger.mergers.competition import CompetitionMerger
from football_data_manager.merger.mergers.fixture import FixtureMerger
from football_data_manager.merger.mergers.match import MatchMerger
from football_data_manager.merger.mergers.match_stat import MatchStatMerger
from football_data_manager.merger.mergers.news import NewsMerger
from football_data_manager.merger.mergers.player import PlayerMerger
from football_data_manager.merger.mergers.player_stat import PlayerStatMerger
from football_data_manager.merger.mergers.season import SeasonMerger
from football_data_manager.merger.mergers.team import GroundMerger, TeamMerger
from football_data_manager.merger.mergers.team_stat import TeamStatMerger
from football_data_manager.merger.scorer import PlayerStatScorer
from football_data_manager.merger.services.resource_validator import (
    ResourceValidationClient,
)
from football_data_manager.merger.services.translator import TranslatorService
from football_data_manager.puller.container import PullerContainer
from football_data_manager.repository.container import RepositoryContainer
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.teams import TeamEntity


def _build_sample_player_stat() -> tuple[PlayerStatEntity, PositionEnum]:
    competition = CompetitionEntity(
        abbreviation="PL",
        name_en="Premier League",
        name_kr="프리미어 리그",
        source_id="8",
    )
    team = TeamEntity(
        abbreviation="ARS",
        icon_url="https://example.com/icon.svg",
        name_en="Arsenal",
        name_kr="아스널",
        short_name_en="Arsenal",
        short_name_kr="아스널",
        source_id="1",
    )
    season = SeasonEntity(
        abbreviation="24/25",
        competition=competition,
        date_start=competition.created_at,
        date_end=competition.created_at,
        season_source_id="578",
        year_start=2024,
        year_end=2025,
    )
    player = PlayerEntity(
        birth_country="England",
        birth_date=None,
        display_name_en="John Doe",
        display_name_kr="존 도",
        full_name="John Doe",
        nationality_en="England",
        nationality_kr="잉글랜드",
        position=PositionEnum.FORWARD,
        preferred_foot=SideEnum.RIGHT,
        source_id="123",
    )

    player_stat = PlayerStatEntity(
        number=9,
        player=player,
        season=season,
        team=team,
        minutes_played=1800,
        shooting_expected_goals_non_penalty=8.2,
        shooting_goals=10,
        shooting_goals_penalty=2,
        shooting_shots=52,
        shooting_shots_on_target=24,
        passing_expected_assists=4.3,
        passing_chances_created=30,
        passing_assists=6,
        passing_passes_successful=680,
        passing_passes_total=820,
        passing_crosses_successful=18,
        passing_crosses_total=49,
        passing_long_balls_accurate=32,
        passing_long_balls_total=71,
        defending_tackles_won=21,
        defending_interceptions=18,
        defending_blocked=12,
        defending_recoveries=90,
        defending_duels_won=120,
        defending_duels_total=210,
        defending_duels_aerial_won=35,
        defending_duels_aerial_total=70,
        defending_fouls_committed=22,
        possession_dribble_successful=51,
        possession_dribble_total=88,
        possession_fouls_won=32,
        possession_touches_in_opposition_box=77,
        discipline_yellow_cards=5,
        discipline_red_cards=0,
        discipline_red_cards_direct=0,
    )
    return player_stat, player.position


def test_phase3_imports() -> None:
    assert TranslatorService is not None
    assert ResourceValidationClient is not None
    assert CompetitionMerger is not None
    assert SeasonMerger is not None
    assert GroundMerger is not None
    assert TeamMerger is not None
    assert PlayerMerger is not None
    assert FixtureMerger is not None
    assert MatchMerger is not None
    assert MatchStatMerger is not None
    assert PlayerStatMerger is not None
    assert TeamStatMerger is not None
    assert AwardMerger is not None
    assert NewsMerger is not None
    assert PlayerStatScorer is not None
    assert MergerContainer is not None


def test_phase3_structure_count_and_empty_inits() -> None:
    merger_root = Path("football_data_manager/merger")
    files = [
        path
        for path in merger_root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    ]
    assert len(files) == 18

    init_files = list(merger_root.rglob("__init__.py"))
    assert all(path.read_text(encoding="utf-8") == "" for path in init_files)


def test_merger_container_provider_smoke() -> None:
    config = ConfigService(Path("configs/.env"))
    repo = RepositoryContainer(config_service=config)
    puller = PullerContainer()
    puller.config.from_dict(config.api_list.model_dump())

    container = MergerContainer(
        config_service=config,
        repository_container=repo,
        puller_container=puller,
    )

    assert container.translator_service() is not None
    assert container.resource_validator() is not None
    assert container.competition_merger() is not None
    assert container.season_merger() is not None
    assert container.team_merger() is not None
    assert container.player_merger() is not None
    assert container.fixture_merger() is not None
    assert container.match_merger() is not None
    assert container.match_stat_merger() is not None
    assert container.player_stat_merger() is not None
    assert container.team_stat_merger() is not None
    assert container.award_merger() is not None
    assert container.news_merger() is not None
    assert container.player_stat_scorer() is not None


def test_player_stat_scorer_score_range() -> None:
    scorer = PlayerStatScorer()
    player_stat, position = _build_sample_player_stat()

    scored = scorer.score(player_stat, position=position)
    for value in [
        scored.score_shooting,
        scored.score_passing,
        scored.score_defending,
        scored.score_dribbling,
        scored.score_discipline,
        scored.score_overall,
    ]:
        assert 0.0 <= value <= 100.0
