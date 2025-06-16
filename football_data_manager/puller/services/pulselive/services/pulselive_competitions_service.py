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
from football_data_manager.puller.services.pulselive.models.responses.compseasons.teams.pulselive_compseason_team_ground_response import (
    PulseliveCompseasonTeamGroundResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.compseasons.teams.pulselive_compseason_team_response import (
    PulseliveCompseasonTeamResponse,
)
from football_data_manager.puller.services.pulselive.services.pulselive_web_client_service import (
    PulseliveWebClientService,
)
from football_data_manager.puller.services.utils.translatorService import (
    TranslatorService,
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
    __translator: TranslatorService

    target_competition_abbr = ["EN_PR"]

    def __init__(
        self,
        db_service: DbService,
        pulselive_service: PulseliveWebClientService,
        translator_service: TranslatorService,
    ):
        self.__competition_repository = CompetitionRepository(db_service)
        self.__ground_repository = GroundRepository(db_service)
        self.__season_repository = SeasonRepository(db_service)
        self.__team_repository = TeamRepository(db_service)
        self.__web_client = pulselive_service
        self.__translator = translator_service

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
        competition = await self.__competition_repository.read_by_source_id(response.id)
        if competition is not None:
            return competition
        else:
            name_kr = await self.__translator.translate_word(response.description)
            competition = CompetitionEntity(
                abbreviation=response.abbreviation,
                name_en=response.description,
                name_kr=name_kr,
                source_id=response.id,
                icon_url=f"https://resources.premierleague.com/premierleague/competitions/competition_{response.id}_small.png",
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
            abbreviation=season_response.label,
            competition=competition,
            date_end=end_datetime,
            date_start=start_datetime,
            source_id=season_response.id,
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

    async def __process_team(
        self,
        team_response: PulseliveCompseasonTeamResponse,
    ) -> tuple[TeamEntity, list[GroundEntity]]:
        grounds = [self.__process_grounds(g) for g in team_response.grounds]
        team = await self.__team_repository.read_by_source_id(team_response.id)
        if team is not None:
            return team, grounds
        else:
            name_kr, short_name_kr = await gather(
                self.__translator.translate_word(team_response.name),
                self.__translator.translate_word(team_response.short_name),
            )
            return (
                TeamEntity(
                    abbreviation=team_response.club.abbr,
                    icon_url=(
                        f"https://resources.premierleague.com/premierleague/badges/50/{team_response.alt_ids['opta']}.png"
                        if "opta" in team_response.alt_ids
                        else None
                    ),
                    name_en=team_response.name,
                    name_kr=name_kr,
                    short_name_en=team_response.short_name,
                    short_name_kr=short_name_kr,
                    source_id=team_response.id,
                ),
                grounds,
            )

    async def __process_grounds(
        self,
        ground_response: PulseliveCompseasonTeamGroundResponse,
    ) -> GroundEntity:
        ground = await self.__ground_repository.read_by_source_id(ground_response.id)
        if ground is not None:
            return ground
        else:
            city_name_kr, name_kr = await gather(
                self.__translator.translate_word(ground_response.city),
                self.__translator.translate_word(ground_response.name),
            )
            return GroundEntity(
                capacity=ground_response.capacity,
                city_name_en=ground_response.city,
                city_name_kr=city_name_kr,
                location_latitude=(
                    ground_response.location.latitude
                    if ground_response.location is not None
                    else None
                ),
                location_longitude=(
                    ground_response.location.longitude
                    if ground_response.location is not None
                    else None
                ),
                name_en=ground_response.name,
                name_kr=name_kr,
                source_id=ground_response.id,
            )
