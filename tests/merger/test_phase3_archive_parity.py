from pathlib import Path


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def test_phase3_archive_parity_anchors() -> None:
    cases = [
        {
            "name": "TranslatorService",
            "current": "football_data_manager/merger/services/translator.py",
            "archive": "archive/football_data_manager/common/services/translator/translatorService.py",
            "current_tokens": [
                "api_list.anthropic.key",
                "translate_word",
                "messages.create",
            ],
            "archive_tokens": [
                "api_list.anthropic.key",
                "translate_word",
                "__translate_from_anthropic",
            ],
        },
        {
            "name": "ResourceValidationClient",
            "current": "football_data_manager/merger/services/resource_validator.py",
            "archive": "archive/football_data_manager/common/services/client/resource_validation_client.py",
            "current_tokens": ["AsyncClient", "validate_url_exists", "head(", "_cache"],
            "archive_tokens": ["AsyncClient", "validate_url_exists", "head(", "__url_cache"],
        },
        {
            "name": "CompetitionMerger",
            "current": "football_data_manager/merger/mergers/competition.py",
            "archive": "archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_competition_puller.py",
            "current_tokens": ["ALLOWED_IDS", "get_by_pulselive_id", "translate_word", "CompetitionEntity"],
            "archive_tokens": ["id_filter", "read_by_pulselive_id", "translate_word", "CompetitionEntity"],
        },
        {
            "name": "SeasonMerger",
            "current": "football_data_manager/merger/mergers/season.py",
            "archive": "archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_season_puller.py",
            "current_tokens": [
                "_extract_year_range",
                "_find_last_matchweek_with_matches",
                "create_utc_from_string",
            ],
            "archive_tokens": [
                "__extract_years_from_season_name",
                "__find_last_matchweek_with_matches",
                "create_utc_from_string",
            ],
        },
        {
            "name": "Team/GroundMerger",
            "current": "football_data_manager/merger/mergers/team.py",
            "archive": "archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_team_puller.py",
            "current_tokens": [
                "GroundEntity.get_source_id",
                "badges-alt",
                "validate_url_exists",
                "append_championship_season",
            ],
            "archive_tokens": [
                "GroundEntity.get_source_id",
                "badges-alt",
                "validate_url_exists",
                "__process_team",
            ],
        },
        {
            "name": "PlayerMerger",
            "current": "football_data_manager/merger/mergers/player.py",
            "archive": "archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_player_puller.py",
            "current_tokens": [
                "get_nationality_kr",
                "110x140/{player_source_id}.png",
                "premierleague/flags/",
            ],
            "archive_tokens": [
                "get_nationality_kr",
                "110x140/{player_id}.png",
                "premierleague/flags/",
            ],
        },
        {
            "name": "FixtureMerger",
            "current": "football_data_manager/merger/mergers/fixture.py",
            "archive": "archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_fixture_puller.py",
            "current_tokens": ["create_utc_from_string", "create_many", "split(\",\")[0]"],
            "archive_tokens": ["create_utc_from_string", "create_all", "split(\",\")[0]"],
        },
        {
            "name": "MatchMerger",
            "current": "football_data_manager/merger/mergers/match.py",
            "archive": "archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_match_puller.py",
            "current_tokens": [
                "pull_match(",
                "pull_match_event",
                "pull_match_lineup",
                "pull_match_official",
                "PeriodEnum.FULLTIME",
                "append_lineup",
                "append_substitute",
                "append_card",
                "append_goal",
                "append_substitution",
            ],
            "archive_tokens": [
                "pull_match(",
                "get_v1_match_event",
                "get_v3_match_lineup",
                "get_v1_match_official",
                "PeriodEnum.FULLTIME",
                "append_lineup",
                "append_substitute",
                "append_card",
                "append_goal",
                "append_substitution",
            ],
        },
        {
            "name": "MatchStatMerger",
            "current": "football_data_manager/merger/mergers/match_stat.py",
            "archive": "archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_match_stat_puller.py",
            "current_tokens": [
                "expected_goals_non_penalty",
                "side.lower() == \"home\"",
                "side.lower() == \"away\"",
                "MatchStatEntity",
            ],
            "archive_tokens": ["expected_goals_non_penalty", "home", "away", "MatchStatEntity"],
        },
        {
            "name": "PlayerStatMerger",
            "current": "football_data_manager/merger/mergers/player_stat.py",
            "archive": "archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_player_stats_puller.py",
            "current_tokens": [
                "goalkeeping_goals_prevented",
                "goalkeeping_penalty_saved",
                "shooting_expected_goals_non_penalty",
            ],
            "archive_tokens": [
                "goalkeeping_goals_prevented",
                "goalkeeping_penalty_saved",
                "shooting_expected_goals_non_penalty",
            ],
        },
        {
            "name": "TeamStatMerger",
            "current": "football_data_manager/merger/mergers/team_stat.py",
            "archive": "archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_team_stats_puller.py",
            "current_tokens": ["PeriodEnum.FULLTIME", "append_match", "overall_stat_defense_saves"],
            "archive_tokens": ["PeriodEnum.FULLTIME", "append_fixtures", "defense_saves"],
        },
        {
            "name": "AwardMerger",
            "current": "football_data_manager/merger/mergers/award.py",
            "archive": "archive/football_data_manager/puller/services/pulselive_new/services/pulselive_new_award_puller.py",
            "current_tokens": ["AwardTypeEnum.from_string", "append_award_association", "_parse_award_date"],
            "archive_tokens": ["AwardTypeEnum.from_string", "append_award_association", "__parse_award_date"],
        },
        {
            "name": "NewsMerger",
            "current": "football_data_manager/merger/mergers/news.py",
            "archive": "archive/football_data_manager/puller/services/the_athletic/the_athletic_puller_service.py",
            "current_tokens": ["__NEXT_DATA__", "application/ld+json", "summary", "append_teams"],
            "archive_tokens": ["__NEXT_DATA__", "application/ld+json", "summary", "append_teams"],
        },
        {
            "name": "PlayerStatScorer",
            "current": "football_data_manager/merger/scorer.py",
            "archive": "archive/legacy_scripts/backfill_player_stat_scores.py",
            "current_tokens": ["PRIOR_MINUTES = 450.0", "OVERALL_PRIOR_MINUTES = 225.0", "POSITION_WEIGHTS"],
            "archive_tokens": ["M0 = 450.0", "M0_OVERALL = 225.0", "POSITION_WEIGHTS"],
        },
    ]

    for case in cases:
        current_source = _read(case["current"])
        archive_source = _read(case["archive"])

        for token in case["current_tokens"]:
            assert token in current_source, f"{case['name']} current missing: {token}"
        for token in case["archive_tokens"]:
            assert token in archive_source, f"{case['name']} archive missing: {token}"


def test_phase3_all_association_paths_present() -> None:
    checks = {
        "football_data_manager/merger/mergers/team.py": ["append_championship_season"],
        "football_data_manager/merger/mergers/player.py": ["append_championship_season"],
        "football_data_manager/merger/mergers/match.py": [
            "append_lineup",
            "append_substitute",
            "append_card",
            "append_goal",
            "append_substitution",
        ],
        "football_data_manager/merger/mergers/team_stat.py": ["append_match"],
        "football_data_manager/merger/mergers/award.py": ["append_award_association"],
        "football_data_manager/merger/mergers/news.py": ["append_teams"],
    }

    for path, tokens in checks.items():
        source = _read(path)
        for token in tokens:
            assert token in source, f"Association token '{token}' missing in {path}"
