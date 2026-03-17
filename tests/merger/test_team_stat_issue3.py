from datetime import datetime

from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.team_stats import TeamStatEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.merger.mergers.team_stat import TeamStatMerger


def _build_competition() -> CompetitionEntity:
    return CompetitionEntity(
        abbreviation="PL",
        name_en="Premier League",
        name_kr="프리미어 리그",
        source_id="8",
    )


def _build_season(competition: CompetitionEntity) -> SeasonEntity:
    return SeasonEntity(
        abbreviation="25/26",
        competition=competition,
        date_start=datetime(2025, 8, 1),
        date_end=datetime(2026, 5, 31),
        season_source_id="2025",
        year_start=2025,
        year_end=2026,
    )


def _build_team() -> TeamEntity:
    return TeamEntity(
        abbreviation="ARS",
        icon_url="https://example.com/icon.svg",
        name_en="Arsenal",
        name_kr="아스널",
        short_name_en="Arsenal",
        short_name_kr="아스널",
        source_id="3",
    )


def test_apply_api_stats_uses_issue3_corrected_field_mapping() -> None:
    competition = _build_competition()
    season = _build_season(competition)
    team = _build_team()
    team_stat = TeamStatEntity(ground=None, season=season, team=team)

    TeamStatMerger._apply_api_stats(
        team_stat,
        {
            "total_shots": 321,
            "blocked_shots": 134,
            "blocks": 79,
            "tackles_won": 284,
            "tackles_lost": 226,
            "corners_taken_incl_short_corners": 181,
        },
    )

    assert team_stat.overall_stat_attack_total_shots == 455
    assert team_stat.overall_stat_defense_blocks == 79
    assert team_stat.overall_stat_defense_tackles == 510
    assert team_stat.overall_stat_defense_tackles_successful == 284
    assert team_stat.overall_stat_attack_corners == 181
