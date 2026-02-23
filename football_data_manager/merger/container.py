from dependency_injector import containers, providers

from football_data_manager.common.services.config.config_service import ConfigService
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


class MergerContainer(containers.DeclarativeContainer):
    """Merger component DI container."""

    config_service = providers.Dependency(instance_of=ConfigService)
    repository_container = providers.DependenciesContainer()
    puller_container = providers.DependenciesContainer()

    translator_service = providers.Singleton(
        TranslatorService,
        config_service=config_service,
    )
    resource_validator = providers.Singleton(ResourceValidationClient)

    competition_merger = providers.Factory(
        CompetitionMerger,
        competition_repo=repository_container.competition_repository,
        translator=translator_service,
    )
    season_merger = providers.Factory(
        SeasonMerger,
        season_repo=repository_container.season_repository,
        fixture_puller=puller_container.fixture_puller,
    )
    team_merger = providers.Factory(
        TeamMerger,
        team_repo=repository_container.team_repository,
        ground_merger=providers.Factory(
            GroundMerger,
            ground_repo=repository_container.ground_repository,
            translator=translator_service,
        ),
        translator=translator_service,
        resource_client=resource_validator,
    )
    player_merger = providers.Factory(
        PlayerMerger,
        player_repo=repository_container.player_repository,
        translator=translator_service,
        resource_client=resource_validator,
    )
    fixture_merger = providers.Factory(
        FixtureMerger,
        fixture_repo=repository_container.fixture_repository,
        team_repo=repository_container.team_repository,
        ground_repo=repository_container.ground_repository,
    )
    match_merger = providers.Factory(
        MatchMerger,
        match_repo=repository_container.match_repository,
        official_repo=repository_container.official_repository,
        player_repo=repository_container.player_repository,
        staff_repo=repository_container.staff_repository,
        translator=translator_service,
        player_puller=puller_container.player_puller,
        match_puller=puller_container.match_puller,
        player_merger=player_merger,
    )
    match_stat_merger = providers.Factory(
        MatchStatMerger,
        match_stat_repo=repository_container.match_stat_repository,
        team_repo=repository_container.team_repository,
    )
    player_stat_merger = providers.Factory(
        PlayerStatMerger,
        player_stat_repo=repository_container.player_stat_repository,
        team_repo=repository_container.team_repository,
        player_puller=puller_container.player_puller,
        player_stat_puller=puller_container.player_stat_puller,
    )
    team_stat_merger = providers.Factory(
        TeamStatMerger,
        team_stat_repo=repository_container.team_stat_repository,
        fixture_repo=repository_container.fixture_repository,
        match_repo=repository_container.match_repository,
        team_stat_puller=puller_container.team_stat_puller,
    )
    award_merger = providers.Factory(
        AwardMerger,
        award_repo=repository_container.award_repository,
        player_repo=repository_container.player_repository,
        player_stat_repo=repository_container.player_stat_repository,
        staff_repo=repository_container.staff_repository,
        translator=translator_service,
    )
    news_merger = providers.Factory(
        NewsMerger,
        news_repo=repository_container.news_repository,
        team_repo=repository_container.team_repository,
        news_puller=puller_container.news_puller,
        config_service=config_service,
    )

    player_stat_scorer = providers.Factory(PlayerStatScorer)
