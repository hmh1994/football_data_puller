from asyncio import gather
from datetime import datetime, timedelta

from football_data_manager.common.repositories.competitions.competition_entity import (
    CompetitionEntity,
)
from football_data_manager.common.repositories.competitions.competition_repository import (
    CompetitionRepository,
)
from football_data_manager.common.repositories.grounds.ground_entity import GroundEntity
from football_data_manager.common.repositories.grounds.ground_repository import (
    GroundRepository,
)
from football_data_manager.common.repositories.seasons.season_entity import SeasonEntity
from football_data_manager.common.repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.common.utils.type_helper.list_helper import remove_duplicates
from football_data_manager.puller.services.pulselive.models.responses.competitions.pulselive_competition_response import (
    PulseliveCompetitionResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.competitions.pulselive_competition_season_response import (
    PulseliveCompetitionSeasonResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.compseasons.teams.pulselive_compseason_team_response import (
    PulseliveCompseasonTeamResponse,
)
from football_data_manager.puller.services.pulselive.services.pulselive_web_client_service import (
    PulseliveWebClientService,
)


class PulseliveCompetitionsService:
    """
    Competitions puller service for Pulselive API.
    :ivar target_competition_abbr: List of target competition abbreviations.
    """

    __competition_repository: CompetitionRepository
    __ground_repository: GroundRepository
    __season_repository: SeasonRepository
    __team_repository: TeamRepository
    __web_client: PulseliveWebClientService

    target_competition_abbr = ["EN_PR"]

    def __init__(
            self,
            db_service: DbService,
            pulselive_service: PulseliveWebClientService,
    ):
        self.__competition_repository = CompetitionRepository(db_service)
        self.__ground_repository = GroundRepository(db_service)
        self.__season_repository = SeasonRepository(db_service)
        self.__team_repository = TeamRepository(db_service)
        self.__web_client = pulselive_service

    async def pull_competitions(self):
        """
        Pulls competitions from the Pulselive API.
        """
        results = await gather(
            *[
                self.__process_competition(c)
                for c in await self.__web_client.get_football_competitions()
                if c.abbreviation in self.target_competition_abbr
            ]
        )
        competitions, seasons_list, teams_list, grounds_list = zip(*results)
        competitions = list(competitions)
        seasons = remove_duplicates(
            [season for seasons in seasons_list for season in seasons],
            key=lambda x: x.id,
        )
        teams = remove_duplicates(
            [team for teams in teams_list for team in teams], key=lambda x: x.id
        )
        grounds = remove_duplicates(
            [ground for grounds in grounds_list for ground in grounds],
            key=lambda x: x.id,
        )
        await self.__season_repository.create_all(seasons, primary_key=lambda x: x.id)
        await self.__competition_repository.create_all(
            competitions, primary_key=lambda x: x.id
        )
        await self.__ground_repository.create_all(grounds, primary_key=lambda x: x.id)
        await self.__team_repository.create_all(teams, primary_key=lambda x: x.id)

    async def __process_competition(
            self,
            response: PulseliveCompetitionResponse,
    ) -> tuple[
        CompetitionEntity, list[SeasonEntity], list[TeamEntity], list[GroundEntity]
    ]:
        """
        Converts Pulselive competitions response to Competition entity.
        :param response: Pulselive competition response.
        :return: Competition entity.
        """
        competition = CompetitionEntity(
            id=CompetitionEntity.get_id(response.id),
            abbreviation=response.abbreviation,
            name_en=response.description,
        )
        results = await gather(
            *[self.__process_season(s, competition) for s in response.comp_seasons]
        )
        season, teams_list, grounds_list = zip(*results)
        return (
            competition,
            list(season),
            [team for teams in teams_list for team in teams],
            [ground for grounds in grounds_list for ground in grounds],
        )

    async def __process_season(
            self,
            season_response: PulseliveCompetitionSeasonResponse,
            competition: CompetitionEntity,
    ) -> tuple[SeasonEntity, list[TeamEntity], list[GroundEntity]]:
        gameweek_response = await self.__web_client.get_football_compseasons_gameweeks(
            season_response.id
        )
        team_responses = await self.__web_client.get_football_compseasons_teams(
            season_response.id
        )
        start = min(gameweek_response.gameweeks, key=lambda gw: gw.gameweek)
        start_datetime = datetime.fromtimestamp(
            start.from_.millis / 1000.0
        ) + timedelta(hours=start.gameweek)
        end = max(gameweek_response.gameweeks, key=lambda gw: gw.gameweek)
        end_datetime = datetime.fromtimestamp(end.from_.millis / 1000.0) + timedelta(
            hours=end.gameweek
        )
        season = SeasonEntity(
            id=SeasonEntity.get_id(season_response.id),
            abbreviation=season_response.label,
            competition_id=competition.id,
            date_end=end_datetime,
            date_start=start_datetime,
            year_end=end_datetime.year,
            year_start=start_datetime.year,
        )
        results = await gather(*[self.__process_team(t) for t in team_responses])
        teams, grounds_list = zip(*results)
        return (
            season,
            list(teams),
            [ground for grounds in grounds_list for ground in grounds],
        )

    @staticmethod
    async def __process_team(
            team_response: PulseliveCompseasonTeamResponse,
    ) -> tuple[TeamEntity, list[GroundEntity]]:
        grounds = [
            GroundEntity(
                id=GroundEntity.get_id(g.id),
                capacity=g.capacity,
                city_name_en=g.city,
                location_latitude=g.location.latitude
                if g.location is not None
                else None,
                location_longitude=g.location.longitude
                if g.location is not None
                else None,
                name_en=g.name,
            )
            for g in team_response.grounds
        ]
        return (
            TeamEntity(
                id=TeamEntity.get_id(team_response.id),
                abbreviation=team_response.club.abbr,
                ground_id=grounds[-1].id,
                icon_url=f"https://resources.premierleague.com/premierleague/badges/50/{team_response.alt_ids['opta']}.png"
                if "opta" in team_response.alt_ids
                else None,
                name_en=team_response.name,
                short_name_en=team_response.short_name,
            ),
            grounds,
        )
