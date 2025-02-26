from asyncio import gather
from datetime import datetime
from itertools import product

from httpx import HTTPStatusError

from football_data_manager.common.repositories.players.player_entity import PlayerEntity
from football_data_manager.common.repositories.players.player_repository import (
    PlayerRepository,
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
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_player_response import (
    PulseliveTeamsCompseasonsStaffPlayerResponse,
)
from football_data_manager.puller.services.pulselive.services.pulselive_web_client_service import (
    PulseliveWebClientService,
)


class PulseliveTeamsPerCompSeasonService:
    __player_repository: PlayerRepository
    __season_repository: SeasonRepository
    __team_repository: TeamRepository
    __web_client: PulseliveWebClientService

    target_season_id = [
        "PULSELIVE_SEASON_719",
    ]

    def __init__(
        self,
        db_service: DbService,
        pulselive_service: PulseliveWebClientService,
    ):
        self.__player_repository = PlayerRepository(db_service)
        self.__season_repository = SeasonRepository(db_service)
        self.__team_repository = TeamRepository(db_service)
        self.__web_client = pulselive_service

    async def pull_players(self):
        seasons: list[SeasonEntity] = await gather(
            *[
                self.__season_repository.read_by_id(season_id)
                for season_id in self.target_season_id
            ]
        )
        # TODO: Filtering team by comp season
        teams: list[TeamEntity] = await self.__team_repository.read_all()
        for season, team in product(seasons, teams):
            players: list[PlayerEntity] = await self.__get_player(season, team)
            if len(players) == 0:
                continue
            await self.__player_repository.create_all(
                players, primary_key=lambda x: x.id
            )

    async def __get_player(
        self, season: SeasonEntity, team: TeamEntity
    ) -> list[PlayerEntity]:
        try:
            response = await self.__web_client.get_football_team_compseason_staff(
                comp_season_id=season.pulselive_id,
                team_id=team.pulselive_id,
            )
            return list(
                filter(
                    None, [self.__convert_player(player) for player in response.players]
                )
            )
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            else:
                raise e

    @staticmethod
    def __convert_player(
        response: PulseliveTeamsCompseasonsStaffPlayerResponse,
    ) -> PlayerEntity | None:
        if response.info.shirt_num is None or response.birth.date is None:
            return None
        else:
            return PlayerEntity(
                id=PlayerEntity.get_id(response.id),
                birth_country=response.birth.country.country,
                birth_date=datetime.fromtimestamp(response.birth.date.millis / 1000.0),
                birth_place=response.birth.place,
                display_name_en=response.name.display,
                full_name=" ".join(
                    filter(
                        None,
                        [response.name.first, response.name.middle, response.name.last],
                    )
                ),
                height=response.height,
                national_team=response.national_team.country
                if response.national_team
                else None,
                photo_url=f"https://resources.premierleague.com/premierleague/photos/players/40x40/{response.alt_ids['opta']}.png"
                if "opta" in response.alt_ids
                else None,
                position=response.info.position,
                position_info_en=response.info.position_info,
                weight=response.weight,
            )
