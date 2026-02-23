from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

from football_data_manager.common.enums.award_type_enum import AwardTypeEnum
from football_data_manager.common.enums.period_enum import PeriodEnum
from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.enums.side_enum import SideEnum
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
from football_data_manager.puller.interfaces.pulselive.v1_match import (
    MatchStatInfoResponse,
    V1MatchTeamStatResponse,
)
from football_data_manager.puller.interfaces.pulselive.v1_player import (
    PlayerDetailResponse,
)
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.entities.matches import MatchEntity
from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.staffs import StaffEntity
from football_data_manager.repository.entities.teams import TeamEntity


class _TranslatorStub:
    def __init__(self):
        self.calls: list[str] = []

    async def translate_word(self, word: str) -> str:
        self.calls.append(word)
        return f"ko-{word}"


class _ResourceValidatorStub:
    async def validate_url_exists(self, url: str) -> bool:
        return True


def _build_competition() -> CompetitionEntity:
    return CompetitionEntity(
        abbreviation="PL",
        name_en="Premier League",
        name_kr="프리미어 리그",
        source_id="8",
    )


def _build_season(competition: CompetitionEntity) -> SeasonEntity:
    return SeasonEntity(
        abbreviation="24/25",
        competition=competition,
        date_start=datetime(2024, 8, 1),
        date_end=datetime(2025, 5, 30),
        season_source_id="2024",
        year_start=2024,
        year_end=2025,
    )


def _build_team(source_id: str, abbr: str, name: str) -> TeamEntity:
    return TeamEntity(
        abbreviation=abbr,
        icon_url="https://example.com/icon.svg",
        name_en=name,
        name_kr=f"ko-{name}",
        short_name_en=name,
        short_name_kr=f"ko-{name}",
        source_id=source_id,
    )


def _build_ground(name_en: str = "Old Trafford") -> GroundEntity:
    return GroundEntity(
        city_name_en="Manchester",
        city_name_kr="맨체스터",
        name_en=name_en,
        name_kr="올드 트래포드",
        capacity=70000,
    )


def _build_player(team: TeamEntity, season: SeasonEntity, source_id: str = "100") -> PlayerEntity:
    _ = team, season
    return PlayerEntity(
        birth_country="England",
        birth_date=datetime(2000, 1, 1),
        display_name_en="John Doe",
        display_name_kr="존 도",
        full_name="John Doe",
        nationality_en="England",
        nationality_kr="잉글랜드",
        position=PositionEnum.FORWARD,
        preferred_foot=SideEnum.RIGHT,
        source_id=source_id,
    )


@pytest.mark.asyncio
async def test_competition_merger_filters_allowed_ids_and_translates() -> None:
    translator = _TranslatorStub()

    class _CompetitionRepo:
        def __init__(self):
            self.by_source_id = {}

        async def get_by_pulselive_id(self, source_id: str):
            return self.by_source_id.get(source_id)

        async def create(self, entity: CompetitionEntity):
            self.by_source_id[entity.source_id] = entity
            return entity

    repo = _CompetitionRepo()
    merger = CompetitionMerger(repo, translator)

    response = SimpleNamespace(
        data=[
            {"id": "1", "code": "PL", "name": "Premier League"},
            {"id": "9999", "code": "X", "name": "Skip Me"},
        ]
    )
    result = await merger.merge(response)

    assert len(result) == 1
    assert result[0].source_id == "1"
    assert result[0].name_kr == "ko-Premier League"
    assert translator.calls == ["Premier League"]


@pytest.mark.asyncio
async def test_season_merger_parses_year_and_finds_last_matchweek() -> None:
    class _SeasonRepo:
        def __init__(self):
            self.by_source_id = {}

        async def get_by_pulselive_id(self, source_id: str):
            return self.by_source_id.get(source_id)

        async def create(self, entity: SeasonEntity):
            self.by_source_id[entity.source_id] = entity
            return entity

    merger = SeasonMerger(_SeasonRepo(), fixture_puller=SimpleNamespace())
    assert merger._extract_year_range("Season 2024/2025") == (2024, 2025)
    assert merger._extract_year_range("Season 24/25") == (2024, 2025)

    async def fake_matches(
        competition_source_id: str, season_source_id: str, matchweek_number: int
    ):
        _ = competition_source_id, season_source_id
        return (
            [{"kickoff": "2024-08-01 20:00:00", "kickoffTimezone": "BST"}]
            if matchweek_number <= 38
            else []
        )

    merger._get_all_matches_for_matchweek = fake_matches  # type: ignore[method-assign]
    last_week, matches = await merger._find_last_matchweek_with_matches("8", "2024", 50)
    assert last_week == 38
    assert len(matches) == 1


@pytest.mark.asyncio
async def test_ground_and_team_merger_create_entities() -> None:
    translator = _TranslatorStub()

    class _GroundRepo:
        def __init__(self):
            self.by_source_id = {}

        async def get_by_pulselive_id(self, source_id: str):
            return self.by_source_id.get(source_id)

        async def create(self, entity: GroundEntity):
            self.by_source_id[entity.source_id] = entity
            return entity

    class _TeamRepo:
        def __init__(self):
            self.by_source_id = {}

        async def get_by_pulselive_id(self, source_id: str):
            return self.by_source_id.get(source_id)

        async def create(self, entity: TeamEntity):
            self.by_source_id[entity.source_id] = entity
            return entity

        async def append_championship_season(self, team: TeamEntity, season: SeasonEntity):
            _ = season
            return team

        async def update(self, team: TeamEntity):
            self.by_source_id[team.source_id] = team
            return team

    competition = _build_competition()
    season = _build_season(competition)

    team_repo = _TeamRepo()
    ground_merger = GroundMerger(_GroundRepo(), translator)
    team_merger = TeamMerger(
        team_repo=team_repo,
        ground_merger=ground_merger,
        translator=translator,
        resource_client=_ResourceValidatorStub(),
    )

    response = SimpleNamespace(
        data=[
            {
                "id": "42",
                "abbr": "MUN",
                "name": "Manchester United",
                "shortName": "Man Utd",
                "stadium": {"name": "Old Trafford", "city": "Manchester", "capacity": 75635},
            }
        ]
    )

    teams, grounds = await team_merger.merge(competition, season, response)
    assert len(teams) == 1
    assert len(grounds) == 1
    assert teams[0].icon_url.endswith("/42.svg")
    assert grounds[0].name_kr == "ko-Old Trafford"
    assert grounds[0].source_id == GroundEntity.get_source_id("Old Trafford")


@pytest.mark.asyncio
async def test_player_merger_country_cache_and_url_validation() -> None:
    translator = _TranslatorStub()

    class _PlayerRepo:
        def __init__(self):
            self.by_source_id = {}

        async def get_by_pulselive_id(self, source_id: str):
            return self.by_source_id.get(source_id)

        async def create(self, entity: PlayerEntity):
            self.by_source_id[entity.source_id] = entity
            return entity

        async def update(self, entity: PlayerEntity):
            self.by_source_id[entity.source_id] = entity
            return entity

        async def append_championship_season(self, player: PlayerEntity, season: SeasonEntity):
            _ = season
            return player

        async def get_nationality_kr(self, nationality_en: str):
            _ = nationality_en
            return None

    player_repo = _PlayerRepo()
    merger = PlayerMerger(
        player_repo=player_repo,
        translator=translator,
        resource_client=_ResourceValidatorStub(),
    )

    assert await merger._get_translated_country("England") == "ko-England"
    assert await merger._get_translated_country("England") == "ko-England"
    assert translator.calls.count("England") == 1

    payload = {
        "country": {"country": "England", "isoCode": "GB", "demonym": None},
        "id": {"playerId": "100"},
        "name": {"simpleName": "John Doe", "fullName": "John Doe"},
        "position": "forward",
        "dates": {"birth": "2000-01-01", "joinedClub": None},
        "preferredFoot": "right",
        "height": 180,
        "weight": 75,
        "countryOfBirth": "England",
        "shirtNum": 9,
    }
    player_detail = PlayerDetailResponse.model_validate(payload)
    merged = await merger.merge_player_detail(player_detail)

    assert merged is not None
    assert merged.nationality_kr == "ko-England"
    assert merged.photo_url is not None and merged.photo_url.endswith("/100.png")
    assert merged.nationality_flag_icon_url is not None


@pytest.mark.asyncio
async def test_fixture_merger_resolves_fk_and_converts_utc() -> None:
    competition = _build_competition()
    season = _build_season(competition)
    home = _build_team("10", "ARS", "Arsenal")
    away = _build_team("20", "LIV", "Liverpool")
    ground = _build_ground("Old Trafford")

    class _FixtureRepo:
        def __init__(self):
            self.by_source_id = {}

        async def get_by_pulselive_id(self, source_id: str):
            return self.by_source_id.get(source_id)

        async def create_many(self, fixtures: list[FixtureEntity]):
            for fixture in fixtures:
                self.by_source_id[fixture.source_id] = fixture
            return fixtures

    class _TeamRepo:
        async def get_by_pulselive_id(self, source_id: str):
            return {"10": home, "20": away}.get(source_id)

    class _GroundRepo:
        async def get_by_name_en(self, name_en: str):
            return ground if name_en == "Old Trafford" else None

    merger = FixtureMerger(_FixtureRepo(), _TeamRepo(), _GroundRepo())
    response = SimpleNamespace(
        data=[
            {
                "matchId": "m-1",
                "homeTeam": {"id": "10"},
                "awayTeam": {"id": "20"},
                "kickoff": "2024-08-16 20:00:00",
                "kickoffTimezone": "BST",
                "ground": "Old Trafford, Manchester",
            }
        ]
    )
    fixtures = await merger.merge(season, 1, response)

    assert len(fixtures) == 1
    assert fixtures[0].home_team_id == home.id
    assert fixtures[0].away_team_id == away.id
    assert fixtures[0].ground_id == ground.id
    assert fixtures[0].kickoff_time.hour == 19


@pytest.mark.asyncio
async def test_match_merger_skips_existing_fulltime_and_helper_methods() -> None:
    competition = _build_competition()
    season = _build_season(competition)
    home = _build_team("10", "ARS", "Arsenal")
    away = _build_team("20", "LIV", "Liverpool")
    fixture = FixtureEntity(
        away_team=away,
        game_week=1,
        home_team=home,
        kickoff_time=datetime(2024, 8, 16, 19, 0, 0),
        season=season,
        source_id="m-1",
    )

    existing = SimpleNamespace(period=PeriodEnum.FULLTIME)

    class _MatchRepo:
        async def get_by_pulselive_id(self, source_id: str):
            _ = source_id
            return existing

    merger = MatchMerger(
        match_repo=_MatchRepo(),
        official_repo=SimpleNamespace(),
        player_repo=SimpleNamespace(),
        staff_repo=SimpleNamespace(),
        translator=_TranslatorStub(),
        player_puller=SimpleNamespace(),
        match_puller=SimpleNamespace(),
        player_merger=SimpleNamespace(),
    )

    assert merger._parse_formation({"formation": "4-3-3"}) == [4, 3, 3]
    assert merger._parse_formation(None) == []
    assert merger._find_formation_position([["10", "20"]], "20") == (0, 1)
    assert merger._to_int("88") == 88
    assert merger._to_int("bad") is None
    assert (
        merger._find_player_detail_for_context(
            [
                SimpleNamespace(id={"competitionId": "8", "seasonId": "2024"}),
                SimpleNamespace(id={"competitionId": "2", "seasonId": "2024"}),
            ],
            competition_source_id="8",
            season_source_id="2024",
        )
        is not None
    )

    merged = await merger.merge(
        fixture=fixture,
        competition=competition,
        season=season,
        match_response=None,  # type: ignore[arg-type]
        event_response=None,  # type: ignore[arg-type]
        lineup_response=None,  # type: ignore[arg-type]
        official_response=None,  # type: ignore[arg-type]
    )
    assert merged is existing


@pytest.mark.asyncio
async def test_match_merger_full_flow_with_4_apis_and_5_associations() -> None:
    competition = _build_competition()
    season = _build_season(competition)
    home = _build_team("10", "ARS", "Arsenal")
    away = _build_team("20", "LIV", "Liverpool")
    fixture = FixtureEntity(
        away_team=away,
        game_week=1,
        home_team=home,
        kickoff_time=datetime(2024, 8, 16, 19, 0, 0),
        season=season,
        source_id="m-2",
    )

    home_starter = _build_player(home, season, source_id="h1")
    home_sub = _build_player(home, season, source_id="h2")
    away_starter = _build_player(away, season, source_id="a1")
    away_sub = _build_player(away, season, source_id="a2")
    player_map = {p.source_id: p for p in [home_starter, home_sub, away_starter, away_sub]}

    class _MatchRepo:
        def __init__(self):
            self.created: MatchEntity | None = None
            self.append_counts = {
                "lineup": 0,
                "substitute": 0,
                "card": 0,
                "goal": 0,
                "substitution": 0,
            }

        async def get_by_pulselive_id(self, source_id: str):
            _ = source_id
            return None

        async def append_lineup(self, match, **kwargs):
            _ = kwargs
            self.append_counts["lineup"] += 1
            return match

        async def append_substitute(self, match, **kwargs):
            _ = kwargs
            self.append_counts["substitute"] += 1
            return match

        async def append_card(self, match, **kwargs):
            _ = kwargs
            self.append_counts["card"] += 1
            return match

        async def append_goal(self, match, **kwargs):
            _ = kwargs
            self.append_counts["goal"] += 1
            return match

        async def append_substitution(self, match, **kwargs):
            _ = kwargs
            self.append_counts["substitution"] += 1
            return match

        async def create(self, match):
            self.created = match
            return match

        async def update(self, match):
            return match

    class _PlayerRepo:
        async def get_by_pulselive_id(self, source_id: str):
            return player_map.get(source_id)

    class _StaffRepo:
        def __init__(self):
            self.created: list[StaffEntity] = []

        async def get_by_pulselive_id(self, source_id: str):
            _ = source_id
            return None

        async def get_by_display_name_en(self, name: str):
            _ = name
            return None

        async def create(self, entity: StaffEntity):
            self.created.append(entity)
            return entity

    class _OfficialRepo:
        def __init__(self):
            self.created = []

        async def get_by_display_name_en(self, name: str):
            _ = name
            return None

        async def create(self, entity):
            self.created.append(entity)
            return entity

    class _MatchPuller:
        def __init__(self):
            self.calls = {"match": 0, "event": 0, "lineup": 0, "official": 0}

        async def pull_match(self, match_id: str):
            _ = match_id
            self.calls["match"] += 1
            return SimpleNamespace(
                attendance=60123,
                awayTeam={"score": 1, "halfTimeScore": 0},
                homeTeam={"score": 2, "halfTimeScore": 1},
                clock="90",
                period="fulltime",
            )

        async def pull_match_event(self, match_id: str):
            _ = match_id
            self.calls["event"] += 1
            return SimpleNamespace(
                homeTeam={
                    "cards": [{"playerId": "h1", "type": "yellow", "time": "10"}],
                    "goals": [
                        {
                            "playerId": "h1",
                            "assistPlayerId": "h2",
                            "goalType": "Penalty",
                            "time": "20",
                        }
                    ],
                    "subs": [{"playerOnId": "h2", "playerOffId": "h1", "time": "60"}],
                },
                awayTeam={
                    "cards": [{"playerId": "a1", "type": "secondyellow", "time": "30"}],
                    "goals": [{"playerId": "a1", "goalType": "Own", "time": "40"}],
                    "subs": [{"playerOnId": "a2", "playerOffId": "a1", "time": "70"}],
                },
            )

        async def pull_match_lineup(self, match_id: str):
            _ = match_id
            self.calls["lineup"] += 1
            return SimpleNamespace(
                homeTeam={
                    "players": [
                        {
                            "id": "h1",
                            "position": "defender",
                            "shirtNum": "4",
                            "isCaptain": True,
                        },
                        {
                            "id": "h2",
                            "position": "Substitute",
                            "shirtNum": "14",
                            "isCaptain": False,
                        },
                    ],
                    "formation": {"formation": "4-3-3", "lineup": [["h1"]]},
                    "managers": [{"id": "m1", "type": "Manager", "display": "Home Boss"}],
                },
                awayTeam={
                    "players": [
                        {
                            "id": "a1",
                            "position": "midfielder",
                            "shirtNum": "8",
                            "isCaptain": True,
                        },
                        {
                            "id": "a2",
                            "position": "substitute",
                            "shirtNum": "18",
                            "isCaptain": False,
                        },
                    ],
                    "formation": {"formation": "4-4-2", "lineup": [["a1"]]},
                    "managers": [{"id": "m2", "type": "Manager", "display": "Away Boss"}],
                },
            )

        async def pull_match_official(self, match_id: str):
            _ = match_id
            self.calls["official"] += 1
            return SimpleNamespace(
                matchOfficials=[
                    {"type": "Referee", "official": {"simpleName": "Ref A", "fullName": "Ref A"}},
                    {
                        "type": "Assistant Referee#1",
                        "official": {"simpleName": "Ref B", "fullName": "Ref B"},
                    },
                    {
                        "type": "Assistant Referee#2",
                        "official": {"simpleName": "Ref C", "fullName": "Ref C"},
                    },
                    {
                        "type": "Fourth official",
                        "official": {"simpleName": "Ref D", "fullName": "Ref D"},
                    },
                    {
                        "type": "Video Assistant Referee",
                        "official": {"simpleName": "Ref E", "fullName": "Ref E"},
                    },
                    {
                        "type": "Assistant VAR Official",
                        "official": {"simpleName": "Ref F", "fullName": "Ref F"},
                    },
                ]
            )

    match_repo = _MatchRepo()
    staff_repo = _StaffRepo()
    official_repo = _OfficialRepo()
    match_puller = _MatchPuller()
    merger = MatchMerger(
        match_repo=match_repo,
        official_repo=official_repo,
        player_repo=_PlayerRepo(),
        staff_repo=staff_repo,
        translator=_TranslatorStub(),
        player_puller=SimpleNamespace(),
        match_puller=match_puller,
        player_merger=SimpleNamespace(),
    )

    merged = await merger.merge_from_api(fixture, competition, season)

    assert merged is not None
    assert match_puller.calls == {"match": 1, "event": 1, "lineup": 1, "official": 1}
    assert len(staff_repo.created) == 2
    assert len(official_repo.created) == 6
    assert match_repo.append_counts["lineup"] == 2
    assert match_repo.append_counts["substitute"] == 2
    assert match_repo.append_counts["card"] == 2
    assert match_repo.append_counts["goal"] == 2
    assert match_repo.append_counts["substitution"] == 2
    assert merged.period == PeriodEnum.FULLTIME


@pytest.mark.asyncio
async def test_match_stat_merger_creates_home_away_entities() -> None:
    competition = _build_competition()
    season = _build_season(competition)
    home = _build_team("10", "ARS", "Arsenal")
    away = _build_team("20", "LIV", "Liverpool")
    fixture = FixtureEntity(
        away_team=away,
        game_week=1,
        home_team=home,
        kickoff_time=datetime(2024, 8, 16, 19, 0, 0),
        season=season,
        source_id="m-1",
    )
    match = MatchEntity(
        attendance=50000,
        away_team_captain=None,
        away_team_manager=None,
        away_team_formation=[4, 3, 3],
        away_team_score=1,
        away_team_half_time_score=0,
        clock=90,
        fixture=fixture,
        home_team_captain=None,
        home_team_manager=None,
        home_team_formation=[4, 3, 3],
        home_team_score=2,
        home_team_half_time_score=1,
        official_main_referee=None,
        official_assistant_1_referee=None,
        official_assistant_2_referee=None,
        official_fourth_referee=None,
        official_var=None,
        official_assistant_var=None,
        period=PeriodEnum.FULLTIME,
    )

    class _TeamRepo:
        async def get_by_pulselive_id(self, source_id: str):
            return {"10": home, "20": away}.get(source_id)

    class _MatchStatRepo:
        def __init__(self):
            self.by_source_id = {}

        async def get_by_pulselive_id(self, source_id: str):
            return self.by_source_id.get(source_id)

        async def create(self, entity):
            self.by_source_id[entity.source_id] = entity
            return entity

        async def update(self, entity):
            self.by_source_id[entity.source_id] = entity
            return entity

    merger = MatchStatMerger(_MatchStatRepo(), _TeamRepo())
    home_stats = MatchStatInfoResponse.model_validate(
        {
            "big_chance_scored": 1,
            "big_chance_missed": 1,
            "expected_goals": 1.2,
            "expected_goals_on_target": 1.0,
            "penalty_faced": 1,
        }
    )
    away_stats = MatchStatInfoResponse.model_validate(
        {
            "big_chance_scored": 0,
            "big_chance_missed": 0,
            "expected_goals": 0.8,
            "expected_goals_on_target": 0.7,
            "penalty_faced": 0,
        }
    )
    response = [
        V1MatchTeamStatResponse(side="home", teamId="10", stats=home_stats),
        V1MatchTeamStatResponse(side="away", teamId="20", stats=away_stats),
    ]
    entities = await merger.merge(match, response)
    assert len(entities) == 2

    home_entity = next(item for item in entities if item.team_id == home.id)
    assert home_entity.big_chances == 2
    assert home_entity.expected_goals_non_penalty == pytest.approx(1.2)


@pytest.mark.asyncio
async def test_player_stat_merger_maps_derived_fields() -> None:
    competition = _build_competition()
    season = _build_season(competition)
    team = _build_team("10", "ARS", "Arsenal")
    player = _build_player(team, season, source_id="100")

    class _TeamRepo:
        async def get_by_pulselive_id(self, source_id: str):
            return team if source_id == "10" else None

    class _PlayerStatRepo:
        async def get_by_pulselive_id(self, source_id: str):
            _ = source_id
            return None

        async def create(self, entity: PlayerStatEntity):
            return entity

        async def update(self, entity: PlayerStatEntity):
            return entity

    class _PlayerPuller:
        async def pull_player_details(self, *args):
            _ = args
            return SimpleNamespace(currentTeam={"id": "10"}, shirtNum=7)

    class _PlayerStatPuller:
        async def pull_player_stats(self, *args):
            _ = args
            return SimpleNamespace(
                stats={
                    "successfulLongPasses": 10,
                    "unsuccessfulLongPasses": 5,
                    "goalAssists": 3,
                    "keyPassesAttemptAssists": 2,
                    "successfulShortPasses": 20,
                    "successfulCrossesAndCorners": 4,
                    "unsuccessfulCrossesAndCorners": 6,
                    "successfulDribbles": 9,
                    "unsuccessfulDribbles": 3,
                    "expectedGoals": 5.0,
                    "penaltiesTaken": 2.0,
                    "totalShots": 30,
                    "blockedShots": 5,
                    "appearances": 12,
                }
            )

    merger = PlayerStatMerger(
        player_stat_repo=_PlayerStatRepo(),
        team_repo=_TeamRepo(),
        player_puller=_PlayerPuller(),
        player_stat_puller=_PlayerStatPuller(),
    )
    merged = await merger.merge(player, competition, season)
    assert merged is not None
    assert merged.source_id == f"{season.source_id}_{player.source_id}"
    assert merged.passing_long_balls_total == 15
    assert merged.passing_chances_created == 5
    assert merged.shooting_shots == 35
    assert merged.shooting_expected_goals_non_penalty == pytest.approx(3.42)


@pytest.mark.asyncio
async def test_team_stat_merger_two_phase_update() -> None:
    competition = _build_competition()
    season = _build_season(competition)
    team = _build_team("10", "ARS", "Arsenal")
    opp = _build_team("20", "LIV", "Liverpool")
    ground = _build_ground()
    fixture = FixtureEntity(
        away_team=opp,
        game_week=1,
        home_team=team,
        kickoff_time=datetime(2024, 8, 16, 19, 0, 0),
        season=season,
        source_id="m-1",
        ground=ground,
    )
    match = MatchEntity(
        attendance=50000,
        away_team_captain=None,
        away_team_manager=None,
        away_team_formation=[4, 3, 3],
        away_team_score=1,
        away_team_half_time_score=0,
        clock=90,
        fixture=fixture,
        home_team_captain=None,
        home_team_manager=None,
        home_team_formation=[4, 3, 3],
        home_team_score=2,
        home_team_half_time_score=1,
        official_main_referee=None,
        official_assistant_1_referee=None,
        official_assistant_2_referee=None,
        official_fourth_referee=None,
        official_var=None,
        official_assistant_var=None,
        period=PeriodEnum.FULLTIME,
    )

    class _TeamStatRepo:
        def __init__(self):
            self.append_count = 0

        async def get_by_pulselive_id(self, source_id: str):
            _ = source_id
            return None

        async def clear_match_associations(self, team_stat):
            _ = team_stat
            return None

        async def append_match(self, team_stat, match, kickoff_time):
            _ = match, kickoff_time
            self.append_count += 1
            return team_stat

        async def create(self, team_stat):
            return team_stat

        async def update(self, team_stat):
            return team_stat

    class _FixtureRepo:
        async def get_by_team_on_season(self, season_obj, team_obj):
            _ = season_obj, team_obj
            return [fixture]

    class _MatchRepo:
        async def get_by_fixture(self, fixture_obj):
            _ = fixture_obj
            return match

    class _TeamStatPuller:
        async def pull_team_stats(self, *args):
            _ = args
            return SimpleNamespace(
                stats={
                    "cornersTakenInclShortCorners": 50,
                    "totalPasses": 1200,
                    "successfulLongPasses": 100,
                    "successfulShortPasses": 900,
                    "unsuccessfulLongPasses": 40,
                    "successfulCrossesAndCorners": 30,
                    "unsuccessfulCrossesAndCorners": 20,
                    "duels": 200,
                    "duelsWon": 120,
                }
            )

    team_stat_repo = _TeamStatRepo()
    merger = TeamStatMerger(
        team_stat_repo=team_stat_repo,
        fixture_repo=_FixtureRepo(),
        match_repo=_MatchRepo(),
        team_stat_puller=_TeamStatPuller(),
    )
    merged = await merger.merge(team, competition, season, ground)
    assert merged is not None
    assert merged.overall_matches == 1
    assert merged.overall_matches_won == 1
    assert merged.overall_points == 3
    assert merged.home_points == 3
    assert merged.overall_stat_attack_corners == 50
    assert merged.overall_stat_attack_passes_successful == 1000
    assert team_stat_repo.append_count == 1


@pytest.mark.asyncio
async def test_award_merger_maps_types_and_associations() -> None:
    competition = _build_competition()
    season = _build_season(competition)
    team = _build_team("10", "ARS", "Arsenal")
    player = _build_player(team, season, source_id="100")
    player_stat = PlayerStatEntity(number=7, player=player, season=season, team=team)
    player_stat.award_associations = []

    translator = _TranslatorStub()

    class _AwardRepo:
        def __init__(self):
            self.by_source_id = {}

        async def get_by_pulselive_id(self, source_id: str):
            return self.by_source_id.get(source_id)

        async def create(self, entity):
            self.by_source_id[entity.source_id] = entity
            return entity

    class _PlayerRepo:
        async def get_by_pulselive_id(self, source_id: str):
            return player if source_id == "100" else None

    class _PlayerStatRepo:
        async def get_by_player_season(self, player_obj, season_obj):
            _ = player_obj, season_obj
            return player_stat

        async def append_award_association(self, player_stat, award, date):
            _ = award, date
            return player_stat

        async def update(self, entity):
            return entity

    class _StaffRepo:
        def __init__(self):
            self.by_source_id = {}

        async def get_by_pulselive_id(self, source_id: str):
            return self.by_source_id.get(source_id)

        async def create(self, entity: StaffEntity):
            self.by_source_id[entity.source_id] = entity
            return entity

        async def append_award_association(self, staff, award, date):
            _ = award, date
            return staff

        async def update(self, entity):
            return entity

    merger = AwardMerger(
        award_repo=_AwardRepo(),
        player_repo=_PlayerRepo(),
        player_stat_repo=_PlayerStatRepo(),
        staff_repo=_StaffRepo(),
        translator=translator,
    )

    assert merger._parse_award_date("2024-9").day == 1
    assert merger._parse_award_date("bad-date") is None

    response = SimpleNamespace(
        playerAwards=[
            {"id": "100", "type": "POTM", "date": "2024-9"},
        ],
        managerAwards=[
            {
                "id": "200",
                "type": "MOTM",
                "date": "2024-9-15",
                "name": {"simpleName": "Mikel Arteta", "fullName": "Mikel Arteta"},
            }
        ],
    )

    awards, player_stats, staffs = await merger.merge(competition, season, response)
    award_types = {award.type for award in awards}
    assert AwardTypeEnum.PLAYER_OF_THE_MONTH in award_types
    assert AwardTypeEnum.MANAGER_OF_THE_MONTH in award_types
    assert len(player_stats) == 1
    assert len(staffs) == 1
    assert staffs[0].display_name_kr == "ko-Mikel Arteta"


@pytest.mark.asyncio
async def test_news_merger_scrape_parse_and_team_resolution() -> None:
    team_a = _build_team("10", "ARS", "Arsenal")
    team_b = _build_team("20", "LIV", "Liverpool")

    class _TeamRepo:
        async def get_all(self):
            return [team_a, team_b]

        async def get_by_abbreviation(self, abbr: str):
            return {"ARS": team_a, "LIV": team_b}.get(abbr)

    merger = NewsMerger(
        news_repo=SimpleNamespace(),
        team_repo=_TeamRepo(),
        news_puller=SimpleNamespace(),
        config_service=SimpleNamespace(
            api_list=SimpleNamespace(anthropic=SimpleNamespace(key=None))
        ),
    )

    html = """
    <html>
      <head>
        <script id="__NEXT_DATA__" type="application/json">
          {"props":{"pageProps":{"article":{"article_body":"Body from next data"}}}}
        </script>
        <script type="application/ld+json">
          {
            "author":[{"name":"John Writer","url":"https://example.com/a","sameAs":null}],
            "dateCreated":"2024-09-10T00:00:00Z",
            "datePublished":"2024-09-10T01:02:03Z",
            "dateModified":"2024-09-10T01:02:03Z",
            "description":"desc",
            "headline":"Headline",
            "thumbnailUrl":"https://example.com/thumb.png"
          }
        </script>
      </head>
      <body></body>
    </html>
    """

    class _FakeResponse:
        text = html

        def raise_for_status(self):
            return None

    async def fake_get(url: str):
        _ = url
        return _FakeResponse()

    merger._http_client.get = fake_get  # type: ignore[method-assign]
    article = await merger._scrape_article("https://example.com/post")
    assert article is not None
    assert article.articleBody == "Body from next data"
    assert article.headline == "Headline"

    parsed = merger._parse_translation_response(
        '{"article":1,"authors":[{"en":"A","ko":"가"}],'
        '"title":{"en":"T","ko":"티"},'
        '"summary":{"en":["s1"],"ko":["요약1"]},"teams":["ARS","ARS","LIV"]}'
    )
    assert parsed.teams == ["ARS", "ARS", "LIV"]
    assert merger._parse_publish_date("2024-09-10T01:02:03Z") is not None

    teams = await merger._resolve_teams(["ARS", "ARS", "LIV", "XXX"])
    assert [team.abbreviation for team in teams] == ["ARS", "LIV"]
    await merger.close()


@pytest.mark.asyncio
async def test_news_merger_merge_league_feed_with_translation_and_team_assoc() -> None:
    team_a = _build_team("10", "ARS", "Arsenal")
    team_b = _build_team("20", "LIV", "Liverpool")

    class _TeamRepo:
        async def get_all(self):
            return [team_a, team_b]

        async def get_by_abbreviation(self, abbr: str):
            return {"ARS": team_a, "LIV": team_b}.get(abbr)

    class _NewsRepo:
        def __init__(self):
            self.created = []

        async def get_by_source(self, source, source_id: str):
            _ = source
            return None

        async def append_teams(self, news, teams):
            news._resolved_teams = list(teams)
            return news

        async def create(self, news):
            self.created.append(news)
            return news

    class _NewsPuller:
        async def pull_league_feed(self, league_abbr: str, page: int):
            _ = league_abbr
            if page > 0:
                return SimpleNamespace(feedMulligan={"layouts": []})
            return SimpleNamespace(
                feedMulligan={
                    "layouts": [
                        {
                            "contents": [
                                {
                                    "consumable_id": "c1",
                                    "permalink": "https://example.com/news-1",
                                }
                            ]
                        }
                    ]
                }
            )

    merger = NewsMerger(
        news_repo=_NewsRepo(),
        team_repo=_TeamRepo(),
        news_puller=_NewsPuller(),
        config_service=SimpleNamespace(
            api_list=SimpleNamespace(anthropic=SimpleNamespace(key=None))
        ),
    )

    async def fake_scrape(permalink: str):
        _ = permalink
        return SimpleNamespace(
            author=[{"name": "Author EN", "url": "https://a", "sameAs": None}],
            dateCreated="2024-09-10T00:00:00Z",
            datePublished="2024-09-10T01:02:03Z",
            dateModified="2024-09-10T01:02:03Z",
            articleBody="Body text",
            description="desc",
            headline="Headline EN",
            thumbnailUrl="https://example.com/thumb.png",
        )

    async def fake_translate(article, team_short_name_map):
        _ = article, team_short_name_map
        return SimpleNamespace(
            authors=[{"en": "Author EN", "ko": "저자"}],
            title={"en": "Headline EN", "ko": "헤드라인"},
            summary={"en": ["s1", "s2"], "ko": ["요약1", "요약2"]},
            teams=["ARS", "ARS", "LIV"],
        )

    merger._scrape_article = fake_scrape  # type: ignore[method-assign]
    merger._translate_article = fake_translate  # type: ignore[method-assign]

    rows = await merger.merge_league_feed(max_pages=2)
    assert len(rows) == 1
    assert rows[0].source_id == "c1"
    assert rows[0].title_kr == "헤드라인"
    assert [team.abbreviation for team in rows[0]._resolved_teams] == ["ARS", "LIV"]
    await merger.close()


def test_player_stat_scorer_weights_and_bayesian_shrinkage() -> None:
    scorer = PlayerStatScorer()

    forward_overall = scorer._score_overall(
        minutes=1200,
        position=PositionEnum.FORWARD,
        shooting=90.0,
        passing=60.0,
        defending=30.0,
        dribbling=80.0,
        discipline=70.0,
    )
    goalkeeper_overall = scorer._score_overall(
        minutes=1200,
        position=PositionEnum.GOALKEEPER,
        shooting=90.0,
        passing=60.0,
        defending=30.0,
        dribbling=80.0,
        discipline=70.0,
    )
    assert forward_overall != goalkeeper_overall

    low_sample = scorer._score_overall(
        minutes=90,
        position=PositionEnum.FORWARD,
        shooting=90.0,
        passing=90.0,
        defending=90.0,
        dribbling=90.0,
        discipline=90.0,
    )
    high_sample = scorer._score_overall(
        minutes=3000,
        position=PositionEnum.FORWARD,
        shooting=90.0,
        passing=90.0,
        defending=90.0,
        dribbling=90.0,
        discipline=90.0,
    )
    assert high_sample > low_sample


def test_player_stat_scorer_constants_match_formula_reference() -> None:
    scorer = PlayerStatScorer()
    assert scorer.PRIOR_MINUTES == 450.0
    assert scorer.OVERALL_PRIOR_MINUTES == 225.0
    assert scorer.PRIOR_MEAN == 0.5
    assert scorer.POSITION_WEIGHTS[PositionEnum.FORWARD] == (0.35, 0.20, 0.05, 0.30, 0.10)
    assert scorer.POSITION_WEIGHTS[PositionEnum.MIDFIELDER] == (0.20, 0.35, 0.15, 0.20, 0.10)
    assert scorer.POSITION_WEIGHTS[PositionEnum.DEFENDER] == (0.05, 0.20, 0.45, 0.10, 0.20)
    assert scorer.POSITION_WEIGHTS[PositionEnum.GOALKEEPER] == (0.00, 0.10, 0.80, 0.00, 0.10)


def test_merger_pattern_has_check_and_upsert_calls() -> None:
    targets = {
        "football_data_manager/merger/mergers/competition.py": ["get_by_pulselive_id", "create("],
        "football_data_manager/merger/mergers/season.py": ["get_by_pulselive_id", "create("],
        "football_data_manager/merger/mergers/team.py": ["get_by_pulselive_id", "create(", "update("],
        "football_data_manager/merger/mergers/player.py": ["get_by_pulselive_id", "create(", "update("],
        "football_data_manager/merger/mergers/fixture.py": ["get_by_pulselive_id", "create_many("],
        "football_data_manager/merger/mergers/match.py": ["get_by_pulselive_id", "create(", "update("],
        "football_data_manager/merger/mergers/match_stat.py": ["get_by_pulselive_id", "create(", "update("],
        "football_data_manager/merger/mergers/player_stat.py": ["get_by_pulselive_id", "create(", "update("],
        "football_data_manager/merger/mergers/team_stat.py": ["get_by_pulselive_id", "create(", "update("],
        "football_data_manager/merger/mergers/award.py": ["get_by_pulselive_id", "create("],
        "football_data_manager/merger/mergers/news.py": ["get_by_source", "create("],
    }

    for path, patterns in targets.items():
        source = Path(path).read_text(encoding="utf-8")
        for pattern in patterns:
            assert pattern in source, f"Pattern '{pattern}' not found in {path}"
