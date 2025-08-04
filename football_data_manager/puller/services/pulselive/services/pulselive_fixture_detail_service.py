from asyncio import gather

from football_data_manager.common.enums.source_enum import SourceEnum
from football_data_manager.common.repositories.competitions.competition_repository import (
    CompetitionRepository,
)
from football_data_manager.common.repositories.fixtures.fixture_entity import (
    FixtureEntity,
)
from football_data_manager.common.repositories.fixtures.fixture_repository import (
    FixtureRepository,
)
from football_data_manager.common.repositories.matches.match_entity import (
    MatchEntity,
)
from football_data_manager.common.repositories.matches.match_repository import (
    MatchRepository,
)
from football_data_manager.common.repositories.officials.official_repository import (
    OfficialRepository,
)
from football_data_manager.common.repositories.players.player_repository import (
    PlayerRepository,
)
from football_data_manager.common.repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.repositories.staffs.staff_repository import (
    StaffRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_player_response import (
    PulseliveFixtureDetailPlayerResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.fixture_details.pulselive_fixture_detail_response import (
    PulseliveFixtureDetailResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.match_stats.pulselive_match_stat_response import (
    PulseliveMatchStatResponse,
)
from football_data_manager.puller.services.pulselive.services.pulselive_web_client_service import (
    PulseliveWebClientService,
)


class PulseliveFixtureDetailService:

    __competition_repository: CompetitionRepository
    __fixture_repository: FixtureRepository
    __match_repository: MatchRepository
    __official_repository: OfficialRepository
    __player_repository: PlayerRepository
    __season_repository: SeasonRepository
    __staff_repository: StaffRepository
    __web_client: PulseliveWebClientService

    target_season_id = [
        "719",
    ]

    def __init__(
        self,
        db_service: DbService,
        pulselive_service: PulseliveWebClientService,
    ):
        self.__competition_repository = CompetitionRepository(db_service)
        self.__fixture_repository = FixtureRepository(db_service)
        self.__match_repository = MatchRepository(db_service)
        self.__official_repository = OfficialRepository(db_service)
        self.__player_repository = PlayerRepository(db_service)
        self.__season_repository = SeasonRepository(db_service)
        self.__staff_repository = StaffRepository(db_service)
        self.__web_client = pulselive_service

    async def pull_fixture_detail(self, fixture: FixtureEntity):
        fixture_detail, match_stat = await gather(
            self.__web_client.get_football_fixture_detail(int(fixture.source_id)),
            self.__web_client.get_football_stats_match(int(fixture.source_id)),
        )

    async def __process_match(
        self,
        fixture: FixtureEntity,
        fixture_detail: PulseliveFixtureDetailResponse,
        match_stat: PulseliveMatchStatResponse,
    ) -> MatchEntity:
        match_base = await self.__process_match_basic_info(
            fixture, fixture_detail, match_stat
        )
        return match_base

    async def __process_match_basic_info(
        self,
        fixture: FixtureEntity,
        fixture_detail: PulseliveFixtureDetailResponse,
        match_stat: PulseliveMatchStatResponse,
    ) -> MatchEntity:
        home_team_detail, away_team_detail = (
            fixture_detail.team_lists[0],
            fixture_detail.team_lists[1],
        )
        home_team_stat, away_team_stat = (
            match_stat.data[home_team_detail.team_id].m,
            match_stat.data[away_team_detail.team_id].m,
        )
        home_captain_id = self.__get_captain(home_team_detail.lineup).player_id
        away_captain_id = self.__get_captain(away_team_detail.lineup).player_id
        home_team_captain, away_team_captain = await gather(
            self.__player_repository.read_by_source_id(
                SourceEnum.PULSELIVE, home_captain_id
            ),
            self.__player_repository.read_by_source_id(
                SourceEnum.PULSELIVE, away_captain_id
            ),
        )
        return MatchEntity(
            attendance=fixture_detail.attendance,
            away_team_captain=away_team_captain,
            away_team_formation=[
                int(f) for f in away_team_detail.formation.label.split("-")
            ],
            away_team_half_time_score=fixture_detail.half_time_score.away_score,
            away_team_score=fixture_detail.teams[1].score,
            away_team_stat_big_chances=self.__get_int_stat(
                away_team_stat, "big_chance_scored"
            )
            + self.__get_int_stat(away_team_stat, "big_chance_missed"),
            home_team_captain=home_team_captain,
            home_team_formation=[
                int(f) for f in home_team_detail.formation.label.split("-")
            ],
            home_team_half_time_score=fixture_detail.half_time_score.home_score,
            home_team_score=fixture_detail.teams[0].score,
        )

    @staticmethod
    def __get_captain(
        players: list[PulseliveFixtureDetailPlayerResponse],
    ) -> PulseliveFixtureDetailPlayerResponse:
        return next(filter(lambda p: p.captain, players))
