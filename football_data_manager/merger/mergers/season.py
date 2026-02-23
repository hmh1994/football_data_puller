from datetime import datetime

from football_data_manager.common.utils.type_helper.datetime_helper import (
    create_utc_from_string,
)
from football_data_manager.puller.interfaces.pulselive.v1_competition import (
    CompetitionDetailSeasonDict,
    V1CompetitionDetailResponse,
)
from football_data_manager.puller.interfaces.pulselive.v1_match import MatchDict
from football_data_manager.puller.pullers.pulselive.fixture import FixturePuller
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.repositories.seasons import SeasonRepository


class SeasonMerger:
    """Merge Pulselive competition-detail season response into season entities."""

    def __init__(
        self,
        season_repo: SeasonRepository,
        fixture_puller: FixturePuller,
    ):
        self._season_repo = season_repo
        self._fixture_puller = fixture_puller

    async def merge(
        self,
        competition: CompetitionEntity,
        response: V1CompetitionDetailResponse,
    ) -> list[SeasonEntity]:
        """Upsert seasons for a competition and derive season boundaries from fixtures."""
        results: list[SeasonEntity] = []

        for item in response.seasons:
            season_source_id = str(item["id"])
            merged_source_id = SeasonEntity.get_source_id(competition, season_source_id)
            existing = await self._season_repo.get_by_pulselive_id(merged_source_id)
            if existing is not None:
                results.append(existing)
                continue

            try:
                year_start, year_end = self._extract_year_range(item["season"])
                date_start = await self._get_season_start_date(
                    competition.source_id, season_source_id
                )
                date_end = await self._get_season_end_date(
                    competition.source_id, season_source_id
                )
            except ValueError:
                continue

            season = SeasonEntity(
                abbreviation=f"{str(year_start)[-2:]}/{str(year_end)[-2:]}",
                competition=competition,
                date_end=date_end,
                date_start=date_start,
                season_source_id=season_source_id,
                year_end=year_end,
                year_start=year_start,
            )
            created = await self._season_repo.create(season)
            if created is not None:
                results.append(created)

        return results

    @staticmethod
    def _extract_year_range(season_name: str) -> tuple[int, int]:
        clean_name = season_name.replace("Season", "").strip()
        parts = clean_name.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid season format: {season_name}")

        year_start = int(parts[0].strip())
        if year_start < 100:
            year_start += 2000

        year_end_str = parts[1].strip()
        if len(year_end_str) == 2:
            year_end = (year_start // 100) * 100 + int(year_end_str)
            if year_end < year_start:
                year_end += 100
        else:
            year_end = int(year_end_str)

        return year_start, year_end

    async def _get_season_start_date(
        self, competition_source_id: str, season_source_id: str
    ) -> datetime:
        matches = await self._get_all_matches_for_matchweek(
            competition_source_id, season_source_id, matchweek_number=1
        )
        if not matches:
            raise ValueError("No matches found for matchweek 1")

        return min(
            create_utc_from_string(match["kickoff"], match["kickoffTimezone"])
            for match in matches
        )

    async def _get_season_end_date(
        self, competition_source_id: str, season_source_id: str
    ) -> datetime:
        _, matches = await self._find_last_matchweek_with_matches(
            competition_source_id, season_source_id, start_week=50
        )
        if not matches:
            raise ValueError("No matches found for season end date")

        return max(
            create_utc_from_string(match["kickoff"], match["kickoffTimezone"])
            for match in matches
        )

    async def _find_last_matchweek_with_matches(
        self,
        competition_source_id: str,
        season_source_id: str,
        start_week: int = 50,
    ) -> tuple[int | None, list[MatchDict]]:
        start_week_matches = await self._get_all_matches_for_matchweek(
            competition_source_id, season_source_id, matchweek_number=start_week
        )
        if start_week_matches:
            current_week = start_week
            current_matches = start_week_matches
            while True:
                next_week_matches = await self._get_all_matches_for_matchweek(
                    competition_source_id,
                    season_source_id,
                    matchweek_number=current_week + 1,
                )
                if not next_week_matches:
                    break
                current_week += 1
                current_matches = next_week_matches
            return current_week, current_matches

        left = 1
        right = start_week
        last_valid_week: int | None = None
        last_valid_matches: list[MatchDict] = []

        while left <= right:
            mid = (left + right) // 2
            mid_matches = await self._get_all_matches_for_matchweek(
                competition_source_id, season_source_id, matchweek_number=mid
            )
            if mid_matches:
                last_valid_week = mid
                last_valid_matches = mid_matches
                left = mid + 1
            else:
                right = mid - 1

        return last_valid_week, last_valid_matches

    async def _get_all_matches_for_matchweek(
        self,
        competition_source_id: str,
        season_source_id: str,
        matchweek_number: int,
    ) -> list[MatchDict]:
        all_matches: list[MatchDict] = []
        next_cursor: str | None = None

        while True:
            response = await self._fixture_puller.pull_matchweek_matches(
                competition_source_id=competition_source_id,
                season_source_id=season_source_id,
                matchweek_number=matchweek_number,
                limit=50,
                _next=next_cursor,
            )
            all_matches.extend(response.data)

            next_cursor = response.pagination.get("_next")
            if next_cursor is None:
                break

        return all_matches

