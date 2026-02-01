from asyncio import gather
from datetime import datetime

from httpx import HTTPStatusError

from football_data_manager.common.repositories.awards.award_entity import (
    AwardEntity,
)
from football_data_manager.common.repositories.awards.award_repository import (
    AwardRepository,
)
from football_data_manager.common.repositories.player_stats.player_stat_entity import (
    PlayerStatEntity,
)
from football_data_manager.common.repositories.player_stats.player_stat_repository import (
    PlayerStatRepository,
)
from football_data_manager.common.repositories.players.player_entity import (
    PlayerEntity,
)
from football_data_manager.common.repositories.players.player_repository import (
    PlayerRepository,
)
from football_data_manager.common.repositories.seasons.season_entity import (
    SeasonEntity,
)
from football_data_manager.common.repositories.seasons.season_repository import (
    SeasonRepository,
)
from football_data_manager.common.repositories.team_stats.team_stat_entity import (
    TeamStatEntity,
)
from football_data_manager.common.repositories.team_stats.team_stat_repository import (
    TeamStatRepository,
)
from football_data_manager.common.repositories.teams.team_entity import TeamEntity
from football_data_manager.common.repositories.teams.team_repository import (
    TeamRepository,
)
from football_data_manager.common.services.db.db_service import DbService
from football_data_manager.common.services.translator.translatorService import (
    TranslatorService,
)
from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_datetime,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_player_award_response import (
    PulseliveTeamsCompseasonsStaffPlayerAwardResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_player_response import (
    PulseliveTeamsCompseasonsStaffPlayerResponse,
)
from football_data_manager.puller.services.pulselive.models.responses.teams.compseasons.pulselive_teams_compseasons_staff_response import (
    PulseliveTeamsCompseasonsStaffResponse,
)
from football_data_manager.puller.services.pulselive.services.pulselive_web_client_service import (
    PulseliveWebClientService,
)


class PulseliveTeamsPerCompSeasonService:
    __award_repository: AwardRepository
    __player_repository: PlayerRepository
    __player_stats_repository: PlayerStatRepository
    __season_repository: SeasonRepository
    __team_repository: TeamRepository
    __team_stats_repository: TeamStatRepository
    __web_client: PulseliveWebClientService
    __translator: TranslatorService

    target_season_id = ["719", "777"]
    championship_key = "CHAMPIONS"

    def __init__(
        self,
        db_service: DbService,
        pulselive_service: PulseliveWebClientService,
        translator_service: TranslatorService,
    ):
        self.__award_repository = AwardRepository(db_service)
        self.__player_repository = PlayerRepository(db_service)
        self.__player_stats_repository = PlayerStatRepository(db_service)
        self.__season_repository = SeasonRepository(db_service)
        self.__team_repository = TeamRepository(db_service)
        self.__team_stats_repository = TeamStatRepository(db_service)
        self.__web_client = pulselive_service
        self.__translator = translator_service

    async def pull_players(self):
        seasons: list[SeasonEntity] = await gather(
            *[
                self.__season_repository.read_by_source_id(season_id)
                for season_id in self.target_season_id
            ]
        )
        for season in seasons:
            team_stats: list[TeamStatEntity] = (
                await self.__team_stats_repository.read_by_season(season)
            )
            teams = [team_stat.team for team_stat in team_stats]
            for team in teams:
                try:
                    response = (
                        await self.__web_client.get_football_team_compseason_staff(
                            comp_season_id=int(season.source_id),
                            team_id=int(team.source_id),
                        )
                    )
                    awards = await self.__get_awards(season, response)
                    await self.__award_repository.create_all(awards)
                    player_infos = await self.__get_player(season, team, response)
                    players, player_stats = zip(*player_infos)
                    await self.__player_repository.create_all(players)
                    await self.__player_stats_repository.create_all(player_stats)
                except HTTPStatusError as e:
                    if e.response.status_code == 404:
                        continue
                    else:
                        raise e

    async def __get_awards(
        self,
        season: SeasonEntity,
        response: PulseliveTeamsCompseasonsStaffResponse,
    ) -> list[AwardEntity]:
        award_info = [
            (key, info)
            for player in response.players
            for key, lst in player.awards.items()
            if key != self.championship_key
            for info in lst
            if str(info.comp_season.id) == season.source_id
        ]
        return await gather(
            *[self.__process_award(season, key, info) for key, info in award_info]
        )

    async def __get_player(
        self,
        season: SeasonEntity,
        team: TeamEntity,
        response: PulseliveTeamsCompseasonsStaffResponse,
    ) -> list[tuple[PlayerEntity, PlayerStatEntity]]:
        player_info = [
            player
            for player in response.players
            if player.info.shirt_num is not None and player.birth.date is not None
        ]
        return await gather(
            *[self.__convert_player(season, team, player) for player in player_info]
        )

    async def __process_award(
        self,
        season: SeasonEntity,
        key: str,
        info: PulseliveTeamsCompseasonsStaffPlayerAwardResponse,
    ) -> AwardEntity:
        name_en = key.lower().replace("_", " ").title()
        date = create_utc_datetime(info.date.year, info.date.month, info.date.day)
        award = self.__award_repository.read_by_source_id(
            AwardEntity.get_source_id(season, name_en, date)
        )
        if award is not None:
            return award
        else:
            name_kr, (description_en, description_kr), icon_url = await gather(
                self.__get_award_name_kr(name_en),
                self.__get_award_description(name_en=name_en),
                self.__award_repository.get_icon_url(name_en=name_en),
            )
            return AwardEntity(
                date=date,
                name_en=name_en,
                name_kr=name_kr,
                season=season,
                description_en=description_en,
                description_kr=description_kr,
                icon_url=icon_url,
            )

    async def __convert_player(
        self,
        season: SeasonEntity,
        team: TeamEntity,
        response: PulseliveTeamsCompseasonsStaffPlayerResponse,
    ) -> tuple[PlayerEntity, PlayerStatEntity]:
        player = await self.__process_player(response)
        player_stat, player = await self.__process_player_stat(
            player, season, team, response
        )
        return player, player_stat

    async def __process_player(
        self,
        response: PulseliveTeamsCompseasonsStaffPlayerResponse,
    ) -> PlayerEntity:
        player = await self.__player_repository.read_by_source_id(response.id)
        if player is not None:
            return player
        else:
            return PlayerEntity(
                birth_country_en=response.birth.country.country,
                birth_country_kr=await self.__get_country_name_kr(
                    response.birth.country.country
                ),
                birth_date=datetime.fromtimestamp(response.birth.date.millis / 1000.0),
                nationality_flag_icon_url=(
                    f"https://resources.premierleague.com/premierleague/flags/{response.birth.country.iso_code}.png"
                    if response.birth.country.iso_code is not None
                    else None
                ),
                birth_place=response.birth.place,
                display_name_en=response.name.display,
                display_name_kr=await self.__translator.translate_word(
                    response.name.display
                ),
                full_name=" ".join(
                    filter(
                        None,
                        [response.name.first, response.name.middle, response.name.last],
                    )
                ),
                height=response.height,
                national_team=(
                    response.national_team.country if response.national_team else None
                ),
                photo_url=(
                    f"https://resources.premierleague.com/premierleague/photos/players/40x40/{response.alt_ids['opta']}.png"
                    if "opta" in response.alt_ids
                    else None
                ),
                position=response.info.position,
                position_info_en=response.info.position_info,
                position_info_kr=await self.__get_position_info_kr(
                    response.info.position_info
                ),
                weight=response.weight,
                source_id=str(response.id),
            )

    async def __process_player_stat(
        self,
        player: PlayerEntity,
        season: SeasonEntity,
        team: TeamEntity,
        response: PulseliveTeamsCompseasonsStaffPlayerResponse,
    ) -> tuple[PlayerStatEntity, PlayerEntity]:
        player_stat = await self.__player_stats_repository.read_by_source_id(
            PlayerStatEntity.get_source_id(season, player)
        )
        if player_stat is not None:
            awards, championship = await self.__pickup_awards_of_player(
                season, response.awards
            )
        else:
            awards, championship = await self.__pickup_awards_of_player(
                season, response.awards
            )
            player_stat = PlayerStatEntity(
                appearances=(
                    response.appearances if response.appearances is not None else 0
                ),
                assists=response.assists if response.assists is not None else 0,
                clean_sheets=(
                    response.clean_sheets if response.clean_sheets is not None else 0
                ),
                goals=response.goals if response.goals is not None else 0,
                goals_conceded=(
                    response.goals_conceded
                    if response.goals_conceded is not None
                    else 0
                ),
                key_passes=(
                    response.key_passes if response.key_passes is not None else 0
                ),
                number=response.info.shirt_num,
                player=player,
                saves=response.saves if response.saves is not None else 0,
                season=season,
                shots=response.shots if response.shots is not None else 0,
                tackles=response.tackles if response.tackles is not None else 0,
                team=team,
            )
        for award in awards:
            player_stat = await self.__player_stats_repository.append_award(
                player_stat, award
            )
        if championship:
            player = await self.__player_repository.update_championship_season(
                player, season
            )
        return player_stat, player

    async def __pickup_awards_of_player(
        self,
        season: SeasonEntity,
        awards: dict[str, list[PulseliveTeamsCompseasonsStaffPlayerAwardResponse]],
    ) -> tuple[list[AwardEntity], bool]:
        award_info = [
            (key, info)
            for key, lst in awards.items()
            for info in lst
            if str(info.comp_season.id) == season.source_id
        ]
        championship = any(key == self.championship_key for key, _ in award_info)
        awards = await gather(
            *[
                self.__award_repository.read_by_source_id(
                    AwardEntity.get_source_id(
                        season,
                        name_en=key.lower().replace("_", " ").title(),
                        date=create_utc_datetime(
                            info.date.year, info.date.month, info.date.day
                        ),
                    )
                )
                for key, info in award_info
                if key != self.championship_key
            ]
        )
        return sorted(awards, key=lambda a: a.date), championship

    async def __get_country_name_kr(self, birth_country_en: str) -> str:
        previous_name = await self.__player_repository.get_nationality_kr(
            birth_country_en=birth_country_en
        )
        if previous_name is not None:
            return previous_name
        else:
            return await self.__translator.translate_word(birth_country_en)

    async def __get_position_info_kr(self, position_info_en: str) -> str:
        previous_name = await self.__player_repository.get_position_info_kr(
            position_info_en=position_info_en
        )
        if previous_name is not None:
            return previous_name
        else:
            return await self.__translator.translate_word(position_info_en)

    async def __get_award_name_kr(self, name_en: str) -> str:
        previous_name = await self.__award_repository.get_award_name_kr(name_en=name_en)
        if previous_name is not None:
            return previous_name
        else:
            return await self.__translator.translate_word(name_en)

    async def __get_award_description(
        self, name_en: str
    ) -> tuple[str | None, str | None]:
        previous_description = await self.__award_repository.get_award_description(
            name_en=name_en
        )
        if previous_description is not None:
            return previous_description
        else:
            return None, None
