from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Configuration, Factory, Singleton

from football_data_manager.puller.clients.pulselive import PulseliveClient
from football_data_manager.puller.clients.the_athletic import TheAthleticClient
from football_data_manager.puller.pullers.pulselive.award import AwardPuller
from football_data_manager.puller.pullers.pulselive.competition import CompetitionPuller
from football_data_manager.puller.pullers.pulselive.fixture import FixturePuller
from football_data_manager.puller.pullers.pulselive.match import MatchPuller
from football_data_manager.puller.pullers.pulselive.match_stat import MatchStatPuller
from football_data_manager.puller.pullers.pulselive.player import PlayerPuller
from football_data_manager.puller.pullers.pulselive.player_stat import PlayerStatPuller
from football_data_manager.puller.pullers.pulselive.season import SeasonPuller
from football_data_manager.puller.pullers.pulselive.team import TeamPuller
from football_data_manager.puller.pullers.pulselive.team_stat import TeamStatPuller
from football_data_manager.puller.pullers.the_athletic.news import NewsPuller


class PullerContainer(DeclarativeContainer):
    """Puller component DI container.

    Manages Clients and Pullers.
    """

    config = Configuration()

    # --- Clients ---

    pulselive_client = Singleton(
        PulseliveClient,
        config=config.pulselive,
    )

    the_athletic_client = Singleton(
        TheAthleticClient,
        config=config.the_athletic,
    )

    # --- Pulselive Pullers ---

    award_puller = Factory(AwardPuller, client=pulselive_client)
    competition_puller = Factory(CompetitionPuller, client=pulselive_client)
    fixture_puller = Factory(FixturePuller, client=pulselive_client)
    match_puller = Factory(MatchPuller, client=pulselive_client)
    match_stat_puller = Factory(MatchStatPuller, client=pulselive_client)
    player_puller = Factory(PlayerPuller, client=pulselive_client)
    player_stat_puller = Factory(PlayerStatPuller, client=pulselive_client)
    season_puller = Factory(SeasonPuller, client=pulselive_client)
    team_puller = Factory(TeamPuller, client=pulselive_client)
    team_stat_puller = Factory(TeamStatPuller, client=pulselive_client)

    # --- The Athletic Pullers ---

    news_puller = Factory(NewsPuller, client=the_athletic_client)
