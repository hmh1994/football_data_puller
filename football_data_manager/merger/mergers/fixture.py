from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_from_string,
)
from football_data_manager.puller.interfaces.pulselive.v1_match import (
    MatchDict,
    V1MatchweekMatchesResponse,
)
from football_data_manager.repository.entities.fixtures import FixtureEntity
from football_data_manager.repository.entities.grounds import GroundEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.teams import TeamEntity
from football_data_manager.repository.repositories.fixtures import FixtureRepository
from football_data_manager.repository.repositories.grounds import GroundRepository
from football_data_manager.repository.repositories.teams import TeamRepository


class FixtureMerger:
    """Merge matchweek matches response into fixture entities."""

    def __init__(
        self,
        fixture_repo: FixtureRepository,
        team_repo: TeamRepository,
        ground_repo: GroundRepository,
    ):
        self._fixture_repo = fixture_repo
        self._team_repo = team_repo
        self._ground_repo = ground_repo

    async def merge(
        self,
        season: SeasonEntity,
        matchweek_number: int,
        response: V1MatchweekMatchesResponse,
    ) -> list[FixtureEntity]:
        """Batch-create fixtures from one matchweek payload."""
        results: list[FixtureEntity] = []
        candidates: list[FixtureEntity] = []

        for match in response.data:
            source_id = str(match["matchId"])
            existing = await self._fixture_repo.get_by_pulselive_id(source_id)
            if existing is not None:
                results.append(existing)
                continue

            fixture = await self._build_fixture(season, matchweek_number, match)
            if fixture is not None:
                candidates.append(fixture)

        if candidates:
            created = await self._fixture_repo.create_many(candidates)
            results.extend(created)

        return results

    async def _build_fixture(
        self,
        season: SeasonEntity,
        matchweek_number: int,
        match: MatchDict,
    ) -> FixtureEntity | None:
        home_team = await self._team_repo.get_by_pulselive_id(str(match["homeTeam"]["id"]))
        away_team = await self._team_repo.get_by_pulselive_id(str(match["awayTeam"]["id"]))
        if home_team is None or away_team is None:
            return None

        kickoff_time = create_utc_from_string(match["kickoff"], match["kickoffTimezone"])

        ground = await self._get_ground(match.get("ground"))

        return FixtureEntity(
            away_team=away_team,
            game_week=matchweek_number,
            home_team=home_team,
            kickoff_time=kickoff_time,
            season=season,
            source_id=str(match["matchId"]),
            ground=ground,
        )

    async def _get_ground(self, ground_name: str | None) -> GroundEntity | None:
        if not ground_name:
            return None
        base_ground_name = ground_name.split(",")[0].strip()
        if not base_ground_name:
            return None
        return await self._ground_repo.get_by_name_en(base_ground_name)
