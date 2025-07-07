from asyncio import run, gather
from typing import TypeVar

from football_data_manager.common.enums.news_type import NewsTypeEnum
from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.new_repositories import Base as NewBase
from football_data_manager.common.new_repositories.base_repository import BaseRepository
from football_data_manager.common.new_repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.new_repositories.competitions.competition_repository import (
    CompetitionRepository,
)
from football_data_manager.common.new_repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.new_repositories.fixtures.fixture_repository import (
    FixtureRepository,
)
from football_data_manager.common.new_repositories.grounds.ground_entity import (
    GroundEntity,
)
from football_data_manager.common.new_repositories.grounds.ground_repository import (
    GroundRepository,
)
from football_data_manager.common.new_repositories.news.news_entity import NewsEntity
from football_data_manager.common.new_repositories.news.news_repository import (
    NewsRepository,
)
from football_data_manager.common.new_repositories.player_stats.player_stat_entity import (
    PlayerStatEntity,
)
from football_data_manager.common.new_repositories.player_stats.player_stat_repository import (
    PlayerStatRepository,
)
from football_data_manager.common.new_repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.new_repositories.players.player_repository import (
    PlayerRepository,
)
from football_data_manager.common.new_repositories.repository_container import (
    CommonRepositoryContainer,
)
from football_data_manager.common.new_repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.new_repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.new_repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)
from football_data_manager.common.new_repositories.team_stats.team_stat_repository import (
    TeamStatRepository,
)
from football_data_manager.common.new_repositories.teams.team_entity import TeamEntity
from football_data_manager.common.new_repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.old_repositories import Base as OldBase
from football_data_manager.common.old_repositories.base_entity import BaseEntity
from football_data_manager.common.old_repositories.competitions.competition_entity import (
    CompetitionEntity as OldCompetitionEntity,
)
from football_data_manager.common.old_repositories.fixtures.fixture_entity import (
    FixtureEntity as OldFixtureEntity,
)
from football_data_manager.common.old_repositories.grounds.ground_entity import (
    GroundEntity as OldGroundEntity,
)
from football_data_manager.common.old_repositories.news.news_entity import (
    NewsEntity as OldNewsEntity,
)
from football_data_manager.common.old_repositories.player_stats.player_stat_entity import (
    PlayerStatEntity as OldPlayerStatEntity,
)
from football_data_manager.common.old_repositories.players.player_entity import (
    PlayerEntity as OldPlayerEntity,
)
from football_data_manager.common.old_repositories.repository_container import (
    CommonRepositoryContainer as OldRepositoryContainer,
)
from football_data_manager.common.old_repositories.seasons.season_entity import (
    SeasonEntity as OldSeasonEntity,
)
from football_data_manager.common.old_repositories.team_stats.team_stat_entity import (
    TeamStatEntity as OldTeamStatEntity,
)
from football_data_manager.common.old_repositories.teams.team_entity import (
    TeamEntity as OldTeamEntity,
)
from football_data_manager.common.old_repositories.teams.team_repository import (
    TeamRepository as OldTeamRepository,
)
from football_data_manager.common.services.common_service_container import (
    CommonServiceContainer,
)
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_datetime,
)

T = TypeVar("T", bound=BaseEntity)


async def get_item(
    source_enum: SourceEnum,
    source_id: str,
    items: list[T],
    repo: BaseRepository[T],
) -> T:
    item = next(
        (
            c
            for c in items
            if c.source_id == source_id and c.source == source_enum.value.upper()
        ),
        None,
    )
    if item is not None:
        return item
    else:
        return await repo.read_by_source_id(source_enum, source_id)


async def map_competition(
    new_comp_repo: CompetitionRepository,
    new_comps: list[CompetitionEntity],
    old_comp: OldCompetitionEntity,
) -> CompetitionEntity:
    comp = await get_item(
        SourceEnum.PULSELIVE, old_comp.source_id, new_comps, new_comp_repo
    )
    if comp is not None:
        return comp
    else:
        return CompetitionEntity(
            abbreviation=old_comp.abbreviation,
            name_en=old_comp.name_en,
            name_kr=old_comp.name_kr,
            source_id=old_comp.source_id,
            icon_url=old_comp.icon_url,
            description_en=old_comp.description_en,
            description_kr=old_comp.description_kr,
        )


async def map_season(
    new_comp_repo: CompetitionRepository,
    new_comps: list[CompetitionEntity],
    new_season_repo: SeasonRepository,
    new_seasons: list[SeasonEntity],
    old_season: OldSeasonEntity,
) -> SeasonEntity:
    season = await get_item(
        SourceEnum.PULSELIVE, old_season.source_id, new_seasons, new_season_repo
    )
    if season is not None:
        return season
    else:
        competition = await get_item(
            SourceEnum.PULSELIVE,
            old_season.competition.source_id,
            new_comps,
            new_comp_repo,
        )
        return SeasonEntity(
            abbreviation=old_season.abbreviation,
            competition=competition,
            date_end=old_season.date_end,
            date_start=old_season.date_start,
            source_id=old_season.source_id,
            year_end=old_season.year_end,
            year_start=old_season.year_start,
        )


async def map_ground(
    new_ground_repo: GroundRepository,
    new_grounds: list[GroundEntity],
    old_ground: OldGroundEntity,
) -> GroundEntity:
    ground = await get_item(
        SourceEnum.PULSELIVE, old_ground.source_id, new_grounds, new_ground_repo
    )
    if ground is not None:
        return ground
    else:
        return GroundEntity(
            city_name_en=old_ground.city_name_en,
            city_name_kr=old_ground.city_name_kr,
            name_en=old_ground.name_en,
            name_kr=old_ground.name_kr,
            source_id=old_ground.source_id,
            capacity=old_ground.capacity,
            location_latitude=old_ground.location_latitude,
            location_longitude=old_ground.location_longitude,
        )


async def map_team(
    new_team_repo: TeamRepository, new_teams: list[TeamEntity], old_team: OldTeamEntity
) -> TeamEntity:
    team = await get_item(
        SourceEnum.PULSELIVE, old_team.source_id, new_teams, new_team_repo
    )
    if team is not None:
        return team
    else:
        return TeamEntity(
            abbreviation=old_team.abbreviation,
            icon_url=old_team.icon_url,
            name_en=old_team.name_en,
            name_kr=old_team.name_kr,
            short_name_en=old_team.short_name_en,
            short_name_kr=old_team.short_name_kr,
            source_id=old_team.source_id,
        )


async def map_fixture(
    new_team_repo: TeamRepository,
    teams: list[TeamEntity],
    new_ground_repo: GroundRepository,
    grounds: list[GroundEntity],
    new_season_repo: SeasonRepository,
    seasons: list[SeasonEntity],
    new_fixture_repo: FixtureRepository,
    new_fixtures: list[FixtureEntity],
    old_fixture: OldFixtureEntity,
) -> FixtureEntity:
    fixture = await get_item(
        SourceEnum.PULSELIVE, old_fixture.source_id, new_fixtures, new_fixture_repo
    )
    if fixture is not None:
        return fixture
    else:
        away_team, home_team, season = await gather(
            get_item(
                SourceEnum.PULSELIVE,
                old_fixture.away_team.source_id,
                teams,
                new_team_repo,
            ),
            get_item(
                SourceEnum.PULSELIVE,
                old_fixture.home_team.source_id,
                teams,
                new_team_repo,
            ),
            get_item(
                SourceEnum.PULSELIVE,
                old_fixture.season.source_id,
                seasons,
                new_season_repo,
            ),
        )
        ground: GroundEntity | None = (
            await get_item(
                SourceEnum.PULSELIVE,
                old_fixture.ground.source_id,
                grounds,
                new_ground_repo,
            )
            if old_fixture.ground is not None
            else None
        )
        return FixtureEntity(
            away_team=away_team,
            game_week=old_fixture.game_week,
            home_team=home_team,
            neutral_ground=old_fixture.neutral_ground,
            kickoff_time=old_fixture.kickoff_time,
            season=season,
            source_id=old_fixture.source_id,
            away_team_score=old_fixture.away_team_score,
            attendance=old_fixture.attendance,
            clock=old_fixture.clock,
            ground=ground,
            home_team_score=old_fixture.home_team_score,
        )


async def map_news(
    old_team_repo: OldTeamRepository,
    new_team_repo: TeamRepository,
    teams: list[TeamEntity],
    new_news_repo: NewsRepository,
    new_news: list[NewsEntity],
    old_news: OldNewsEntity,
) -> NewsEntity:
    news = await get_item(
        SourceEnum.PULSELIVE, old_news.source_id, new_news, new_news_repo
    )
    if news is not None:
        return news
    else:
        old_teams_in_news = await gather(
            *[old_team_repo.read_by_id(team_id) for team_id in old_news.teams]
        )
        new_teams_in_news = await gather(
            *[
                get_item(
                    SourceEnum.PULSELIVE,
                    old_team.source_id,
                    teams,
                    new_team_repo,
                )
                for old_team in old_teams_in_news
            ]
        )
        return NewsEntity(
            author_en=old_news.author_en,
            author_kr=old_news.author_kr,
            content_en=old_news.content_en,
            content_kr=old_news.content_kr,
            publish_date=old_news.publish_date,
            url=old_news.url,
            source=(
                old_news.source
                if isinstance(old_news.source, SourceEnum)
                else SourceEnum.from_string(old_news.source)
            ),
            source_id=old_news.source_id,
            teams=new_teams_in_news,
            thumbnail_url=old_news.thumbnail_url,
            title_en=old_news.title_en,
            title_kr=old_news.title_kr,
            typ=(
                old_news.type
                if isinstance(old_news.type, NewsTypeEnum)
                else NewsTypeEnum.from_string(old_news.type)
            ),
        )


async def map_team_stat(
    new_team_repo: TeamRepository,
    new_teams: list[TeamEntity],
    new_season_repo: SeasonRepository,
    new_seasons: list[SeasonEntity],
    new_ground_repo: GroundRepository,
    new_grounds: list[GroundEntity],
    new_fixtures: list[FixtureEntity],
    new_team_stat_repo: TeamStatRepository,
    new_team_stats: list[TeamStatEntity],
    old_team_stat: OldTeamStatEntity,
) -> TeamStatEntity:
    team_stat = await get_item(
        SourceEnum.PULSELIVE,
        old_team_stat.source_id,
        new_team_stats,
        new_team_stat_repo,
    )
    if team_stat is not None:
        return team_stat
    else:
        team, season, ground = await gather(
            get_item(
                SourceEnum.PULSELIVE,
                old_team_stat.team.source_id,
                new_teams,
                new_team_repo,
            ),
            get_item(
                SourceEnum.PULSELIVE,
                old_team_stat.season.source_id,
                new_seasons,
                new_season_repo,
            ),
            get_item(
                SourceEnum.PULSELIVE,
                old_team_stat.ground.source_id if old_team_stat.ground else "",
                new_grounds,
                new_ground_repo,
            ),
        )
        fixtures = [
            fixture
            for fixture in new_fixtures
            if (fixture.home_team_id == team.id or fixture.away_team_id == team.id)
            and fixture.season_id == season.id
        ]
        fixtures.sort(key=lambda f: f.kickoff_time)
        team_stat = TeamStatEntity(ground, season, team)
        for fixture in fixtures:
            team_stat.apply_fixture(fixture)
        return team_stat


async def map_player(
    new_player_repo: PlayerRepository,
    new_players: list[PlayerEntity],
    old_player: OldPlayerEntity,
) -> PlayerEntity:
    player = await get_item(
        SourceEnum.PULSELIVE, old_player.source_id, new_players, new_player_repo
    )
    if player is not None:
        return player
    else:
        return PlayerEntity(
            birth_country_en=old_player.birth_country_en,
            birth_country_kr=old_player.birth_country_kr,
            birth_date=create_utc_datetime(
                year=old_player.birth_date.year,
                month=old_player.birth_date.month,
                day=old_player.birth_date.day,
            ),
            birth_country_flag_icon_url=old_player.birth_country_flag_icon_url,
            display_name_en=old_player.display_name_en,
            display_name_kr=old_player.display_name_kr,
            full_name=old_player.full_name,
            position=old_player.position,
            position_info_en=old_player.position_info_en,
            position_info_kr=old_player.position_info_kr,
            source_id=old_player.source_id,
            birth_place=old_player.birth_place,
            height=old_player.height,
            national_team=old_player.national_team,
            photo_url=old_player.photo_url,
            weight=old_player.weight,
        )


async def map_player_stat(
    new_team_repo: TeamRepository,
    new_teams: list[TeamEntity],
    new_season_repo: SeasonRepository,
    new_seasons: list[SeasonEntity],
    new_player_repo: PlayerRepository,
    new_players: list[PlayerEntity],
    new_player_stat_repo: PlayerStatRepository,
    new_player_stats: list[PlayerStatEntity],
    old_player_stat: OldPlayerStatEntity,
) -> PlayerStatEntity:
    player_stat = await get_item(
        SourceEnum.PULSELIVE,
        old_player_stat.source_id,
        new_player_stats,
        new_player_stat_repo,
    )
    if player_stat is not None:
        return player_stat
    else:
        team, season, player = await gather(
            get_item(
                SourceEnum.PULSELIVE,
                old_player_stat.team.source_id,
                new_teams,
                new_team_repo,
            ),
            get_item(
                SourceEnum.PULSELIVE,
                old_player_stat.season.source_id,
                new_seasons,
                new_season_repo,
            ),
            get_item(
                SourceEnum.PULSELIVE,
                old_player_stat.player.source_id,
                new_players,
                new_player_repo,
            ),
        )
        return PlayerStatEntity(
            appearances=old_player_stat.appearances,
            assists=old_player_stat.assists,
            clean_sheets=old_player_stat.clean_sheets,
            goals=old_player_stat.goals,
            goals_conceded=old_player_stat.goals_conceded,
            key_passes=old_player_stat.key_passes,
            number=old_player_stat.number,
            player=player,
            saves=old_player_stat.saves,
            season=season,
            shots=old_player_stat.shots,
            tackles=old_player_stat.tackles,
            team=team,
        )


async def runrun():

    common_service_container = CommonServiceContainer()
    common_service_container.container_config.from_dict(
        {"config_path": "./configs/.env"}
    )
    config_service = common_service_container.config_service()
    db_service = common_service_container.db_service()
    async with db_service.engine.begin() as conn:
        await conn.run_sync(OldBase.metadata.create_all)
        await conn.run_sync(NewBase.metadata.create_all)
    old_repo = OldRepositoryContainer(db_service=db_service)
    new_repo = CommonRepositoryContainer(db_service=db_service)
    #
    old_competitions = await old_repo.competition_repository().read_all()
    old_fixtures = await old_repo.fixture_repository().read_all()
    old_grounds = await old_repo.ground_repository().read_all()
    old_news = await old_repo.news_repository().read_all()
    old_player_stats = await old_repo.player_stat_repository().read_all()
    old_players = await old_repo.player_repository().read_all()
    old_seasons = await old_repo.season_repository().read_all()
    old_team_stats = await old_repo.team_stat_repository().read_all()
    old_teams = await old_repo.team_repository().read_all()
    # Create new competitions
    print("Old competitions:", len(old_competitions))
    new_comp_repo = new_repo.competition_repository()
    new_comps = await new_comp_repo.read_all()
    new_comps = await gather(
        *[map_competition(new_comp_repo, new_comps, comp) for comp in old_competitions]
    )
    await new_comp_repo.create_all(new_comps)
    print("New competitions:", await new_comp_repo.count())
    # Create new grounds
    print("Old grounds:", len(old_grounds))
    new_ground_repo = new_repo.ground_repository()
    new_grounds = await new_ground_repo.read_all()
    new_grounds = await gather(
        *[map_ground(new_ground_repo, new_grounds, ground) for ground in old_grounds]
    )
    await new_ground_repo.create_all(new_grounds)
    print("New grounds:", await new_ground_repo.count())
    # Create new seasons
    print("Old seasons:", len(old_seasons))
    new_season_repo = new_repo.season_repository()
    new_seasons = await new_season_repo.read_all()
    new_seasons = await gather(
        *[
            map_season(new_comp_repo, new_comps, new_season_repo, new_seasons, season)
            for season in old_seasons
        ]
    )
    await new_season_repo.create_all(new_seasons)
    print("New seasons:", await new_season_repo.count())
    # Create new teams
    print("Old teams:", len(old_teams))
    new_team_repo = new_repo.team_repository()
    new_teams = await new_team_repo.read_all()
    new_teams = await gather(
        *[map_team(new_team_repo, new_teams, team) for team in old_teams]
    )
    await new_team_repo.create_all(new_teams)
    print("New teams:", await new_team_repo.count())
    # Create new fixtures
    print("Old fixtures:", len(old_fixtures))
    new_fixture_repo = new_repo.fixture_repository()
    new_fixtures = await new_fixture_repo.read_all()
    new_fixtures = await gather(
        *[
            map_fixture(
                new_team_repo,
                new_teams,
                new_ground_repo,
                new_grounds,
                new_season_repo,
                new_seasons,
                new_fixture_repo,
                new_fixtures,
                fixture,
            )
            for fixture in old_fixtures
        ]
    )
    await new_fixture_repo.create_all(new_fixtures)
    print("New fixtures:", await new_fixture_repo.count())
    # Create new news
    print("Old news:", len(old_news))
    new_news_repo = new_repo.news_repository()
    new_news = await new_news_repo.read_all()
    new_news = await gather(
        *[
            map_news(
                old_repo.team_repository(),
                new_team_repo,
                new_teams,
                new_news_repo,
                new_news,
                news,
            )
            for news in old_news
        ]
    )
    await new_news_repo.create_all(new_news)
    print("New news:", await new_news_repo.count())
    # Create team stats
    print("Old team stats:", len(old_team_stats))
    new_team_stat_repo = new_repo.team_stat_repository()
    new_team_stats = await new_team_stat_repo.read_all()
    new_team_stats: list[TeamStatEntity] = await gather(
        *[
            map_team_stat(
                new_team_repo,
                new_teams,
                new_season_repo,
                new_seasons,
                new_ground_repo,
                new_grounds,
                new_fixtures,
                new_team_stat_repo,
                new_team_stats,
                team_stat,
            )
            for team_stat in old_team_stats
        ]
    )
    for team_stat in new_team_stats:
        await team_stat.apply_position(db_service, new_team_stats)
    await new_team_stat_repo.create_all(new_team_stats)
    print("New team stats:", await new_team_stat_repo.count())
    # Update teams with new stats
    for team_stat in new_team_stats:
        if team_stat.overall_position == 1 and team_stat.overall_matches == 38:
            async with db_service.create_db_session() as session:
                merged_entity = await session.merge(team_stat)
                await session.refresh(merged_entity, ["team", "season"])
                team: TeamEntity = merged_entity.team
                season: SeasonEntity = merged_entity.season
                merged_entity = await session.merge(team)
                await session.refresh(
                    merged_entity, ["championship_season_associations"]
                )
                championship_season_associations = (
                    merged_entity.championship_season_associations
                )
            if any(
                season.id == season_id for season_id in championship_season_associations
            ):
                continue
            new_team = await team.update_championship_season(db_service, season)
            await new_team_repo.update(new_team)
            print(
                f"Updated team {new_team.name_en} with championship season {season.abbreviation}"
            )
    # Create players
    print("Old players:", len(old_players))
    new_player_repo = new_repo.player_repository()
    new_players = await new_player_repo.read_all()
    new_players = await gather(
        *[map_player(new_player_repo, new_players, player) for player in old_players]
    )
    await new_player_repo.create_all(new_players)
    print("New players:", await new_player_repo.count())
    # Print counts
    print("Old player stats:", len(old_player_stats))
    new_player_stat_repo = new_repo.player_stat_repository()
    new_player_stats = await new_player_stat_repo.read_all()
    new_player_stats = await gather(
        *[
            map_player_stat(
                new_team_repo,
                new_teams,
                new_season_repo,
                new_seasons,
                new_player_repo,
                new_players,
                new_player_stat_repo,
                new_player_stats,
                player_stat,
            )
            for player_stat in old_player_stats
        ]
    )
    await new_player_stat_repo.create_all(new_player_stats)
    print("New players stats:", await new_player_stat_repo.count())


run(runrun())
