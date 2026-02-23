from football_data_manager.common.enums.position_enum import PositionEnum
from football_data_manager.common.enums.side_enum import SideEnum
from football_data_manager.merger.services.resource_validator import (
    ResourceValidationClient,
)
from football_data_manager.merger.services.translator import TranslatorService
from football_data_manager.merger.utils import is_updated_within
from football_data_manager.puller.interfaces.pulselive.v1_player import PlayerDetailResponse
from football_data_manager.puller.interfaces.pulselive.v2_player import V2SquadResponse
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.players import PlayerEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.repositories.players import PlayerRepository


class PlayerMerger:
    """Merge player squad/detail responses into player entities."""

    def __init__(
        self,
        player_repo: PlayerRepository,
        translator: TranslatorService,
        resource_client: ResourceValidationClient,
    ):
        self._player_repo = player_repo
        self._translator = translator
        self._resource_client = resource_client
        self._country_cache: dict[str, str] = {}

    async def merge(
        self,
        competition: CompetitionEntity,
        season: SeasonEntity,
        team: TeamEntity,
        response: V2SquadResponse,
    ) -> list[PlayerEntity]:
        """Merge squad players and append season championship association."""
        if season.competition_id != competition.id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        players: list[PlayerEntity] = []
        for player_item in response.players:
            player = await self.merge_player_detail(player_item, season)
            if player is None:
                continue
            player = await self._player_repo.append_championship_season(player, season)
            player = await self._player_repo.update(player)
            players.append(player)

        return players

    async def merge_player_detail(
        self,
        player_item: PlayerDetailResponse,
        season: SeasonEntity | None = None,
    ) -> PlayerEntity | None:
        """Merge one player detail payload. Reused for lineup fallback creation."""
        source_id = player_item.id["player_id"]
        existing = await self._player_repo.get_by_pulselive_id(source_id)
        if existing is not None:
            if is_updated_within(existing):
                return existing

            if not existing.photo_url:
                photo_url = await self._validate_player_photo(source_id)
                if photo_url:
                    existing.photo_url = photo_url
                    existing = await self._player_repo.update(existing)

            if season is not None:
                existing = await self._player_repo.append_championship_season(
                    existing, season
                )
                existing = await self._player_repo.update(existing)

            return existing

        display_name_en = player_item.name["display"].strip()
        if not display_name_en:
            return None

        nationality_en = player_item.country["country"]
        nationality_kr = await self._get_translated_country(nationality_en)

        position = PositionEnum.from_string(player_item.position)
        preferred_foot = SideEnum.from_string(player_item.preferred_foot)

        player = PlayerEntity(
            birth_country=player_item.country_of_birth,
            birth_date=player_item.dates.birth,
            display_name_en=display_name_en,
            display_name_kr=await self._translator.translate_word(display_name_en),
            full_name=f"{player_item.name['first']} {player_item.name['last']}",
            nationality_en=nationality_en,
            nationality_kr=nationality_kr,
            nationality_flag_icon_url=await self._validate_flag_url(
                player_item.country.get("iso_code")
            ),
            position=position,
            preferred_foot=preferred_foot,
            source_id=source_id,
            height=player_item.height,
            weight=player_item.weight,
            photo_url=await self._validate_player_photo(source_id),
        )

        created = await self._player_repo.create(player)
        if created is None:
            created = await self._player_repo.get_by_pulselive_id(source_id)
            if created is None:
                return None

        if season is not None:
            created = await self._player_repo.append_championship_season(created, season)
            created = await self._player_repo.update(created)

        return created

    async def _get_translated_country(self, country_en: str) -> str:
        if country_en in self._country_cache:
            return self._country_cache[country_en]

        existing = await self._player_repo.get_nationality_kr(country_en)
        if existing:
            self._country_cache[country_en] = existing
            return existing

        translated = await self._translator.translate_word(country_en)
        self._country_cache[country_en] = translated
        return translated

    async def _validate_player_photo(self, player_source_id: str) -> str | None:
        photo_url = (
            "https://resources.premierleague.com/premierleague25/photos/players/"
            f"110x140/{player_source_id}.png"
        )
        if await self._resource_client.validate_url_exists(photo_url):
            return photo_url
        return None

    async def _validate_flag_url(self, iso_code: str | None) -> str | None:
        if not iso_code:
            return None

        flag_url = (
            "https://resources.premierleague.com/"
            f"premierleague/flags/{iso_code}.png"
        )
        if await self._resource_client.validate_url_exists(flag_url):
            return flag_url
        return None
