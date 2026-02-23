from football_data_manager.merger.services.resource_validator import (
    ResourceValidationClient,
)
from football_data_manager.merger.services.translator import TranslatorService
from football_data_manager.puller.interfaces.pulselive.v1_team import TeamItemDict, V1TeamsResponse
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.repositories.grounds import GroundRepository
from football_data_manager.repository.repositories.teams import TeamRepository
from football_data_manager.merger.utils import is_updated_within


class GroundMerger:
    """Merge stadium information in team response into ground entities."""

    def __init__(
        self,
        ground_repo: GroundRepository,
        translator: TranslatorService,
    ):
        self._ground_repo = ground_repo
        self._translator = translator

    async def merge_from_team_item(self, item: TeamItemDict) -> GroundEntity | None:
        """Create or get ground entity from one team response item."""
        stadium = item.get("stadium")
        if not stadium:
            return None

        ground_name = stadium.get("name")
        if not ground_name:
            return None

        source_id = GroundEntity.get_source_id(ground_name)
        existing = await self._ground_repo.get_by_pulselive_id(source_id)
        if existing is not None:
            return existing

        city_name_en = stadium.get("city") or "Unknown"
        ground = GroundEntity(
            city_name_en=city_name_en,
            city_name_kr=await self._translator.translate_word(city_name_en),
            name_en=ground_name,
            name_kr=await self._translator.translate_word(ground_name),
            capacity=stadium.get("capacity"),
        )
        return await self._ground_repo.create(ground)


class TeamMerger:
    """Merge Pulselive team response into team entities."""

    def __init__(
        self,
        team_repo: TeamRepository,
        ground_merger: GroundMerger,
        translator: TranslatorService,
        resource_client: ResourceValidationClient,
    ):
        self._team_repo = team_repo
        self._ground_merger = ground_merger
        self._translator = translator
        self._resource_client = resource_client

    async def merge(
        self,
        competition: CompetitionEntity,
        season: SeasonEntity,
        response: V1TeamsResponse,
    ) -> tuple[list[TeamEntity], list[GroundEntity]]:
        """Merge teams and grounds in order, then attach season associations."""
        if season.competition_id != competition.id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        teams: list[TeamEntity] = []
        grounds: list[GroundEntity] = []

        for item in response.data:
            ground = await self._ground_merger.merge_from_team_item(item)
            if ground is not None:
                grounds.append(ground)

            team = await self._merge_team(item, season)
            if team is not None:
                teams.append(team)

        return teams, grounds

    async def _merge_team(
        self,
        item: TeamItemDict,
        season: SeasonEntity,
    ) -> TeamEntity | None:
        source_id = str(item["id"])
        existing = await self._team_repo.get_by_pulselive_id(source_id)
        if existing is not None:
            if is_updated_within(existing):
                return existing

            if not existing.icon_url:
                icon_url = await self._validate_team_icon_url(source_id)
                if icon_url:
                    existing.icon_url = icon_url
                    existing = await self._team_repo.update(existing)

            existing = await self._team_repo.append_championship_season(existing, season)
            return await self._team_repo.update(existing)

        name_en = item["name"]
        short_name_en = item.get("short_name") or name_en
        icon_url = await self._validate_team_icon_url(source_id)

        team = TeamEntity(
            abbreviation=item["abbr"],
            icon_url=icon_url or "",
            name_en=name_en,
            name_kr=await self._translator.translate_word(name_en),
            short_name_en=short_name_en,
            short_name_kr=await self._translator.translate_word(short_name_en),
            source_id=source_id,
        )
        created = await self._team_repo.create(team)
        if created is None:
            return await self._team_repo.get_by_pulselive_id(source_id)

        created = await self._team_repo.append_championship_season(created, season)
        return await self._team_repo.update(created)

    async def _validate_team_icon_url(self, team_source_id: str) -> str | None:
        badge_url = (
            "https://resources.premierleague.com/"
            f"premierleague25/badges-alt/{team_source_id}.svg"
        )
        if await self._resource_client.validate_url_exists(badge_url):
            return badge_url
        return None
