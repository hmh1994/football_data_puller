from datetime import UTC, datetime

from football_data_manager.common.enums.award_type_enum import AwardTypeEnum
from football_data_manager.merger.services.translator import TranslatorService
from football_data_manager.puller.interfaces.pulselive.v1_award import (
    ManagerAwardDict,
    PlayerAwardDict,
    V1AwardResponse,
)
from football_data_manager.repository.entities.awards import AwardEntity
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.entities.player_stats import PlayerStatEntity
from football_data_manager.repository.entities.seasons import SeasonEntity
from football_data_manager.repository.entities.staffs import StaffEntity
from football_data_manager.repository.repositories.awards import AwardRepository
from football_data_manager.repository.repositories.player_stats import PlayerStatRepository
from football_data_manager.repository.repositories.players import PlayerRepository
from football_data_manager.repository.repositories.staffs import StaffRepository


class AwardMerger:
    """Merge season award payload into award/staff/player-stat associations."""

    def __init__(
        self,
        award_repo: AwardRepository,
        player_repo: PlayerRepository,
        player_stat_repo: PlayerStatRepository,
        staff_repo: StaffRepository,
        translator: TranslatorService,
    ):
        self._award_repo = award_repo
        self._player_repo = player_repo
        self._player_stat_repo = player_stat_repo
        self._staff_repo = staff_repo
        self._translator = translator

    async def merge(
        self,
        competition: CompetitionEntity,
        season: SeasonEntity,
        response: V1AwardResponse,
    ) -> tuple[list[AwardEntity], list[PlayerStatEntity], list[StaffEntity]]:
        """Upsert awards and append player-stat/staff award associations."""
        if season.competition_id != competition.id:
            raise ValueError(
                f"Season {season.id} does not belong to competition {competition.id}"
            )

        awards: dict[str, AwardEntity] = {}
        updated_player_stats: dict[str, PlayerStatEntity] = {}
        updated_staffs: dict[str, StaffEntity] = {}

        for item in response.playerAwards:
            award = await self._get_or_create_award(item)
            if award is None:
                continue
            awards[award.id] = award

            player_stat = await self._get_player_stat_for_award(item, season)
            if player_stat is None:
                continue

            award_date = self._parse_award_date(item["date"])
            if award_date is None:
                continue

            updated = await self._player_stat_repo.append_award_association(
                player_stat=player_stat,
                award=award,
                date=award_date,
            )
            updated = await self._player_stat_repo.update(updated)
            updated_player_stats[updated.id] = updated

        for item in response.managerAwards:
            award = await self._get_or_create_award(item)
            if award is None:
                continue
            awards[award.id] = award

            staff = await self._get_or_create_staff(item)
            if staff is None:
                continue

            award_date = self._parse_award_date(item["date"])
            if award_date is None:
                continue

            updated = await self._staff_repo.append_award_association(
                staff=staff,
                award=award,
                date=award_date,
            )
            updated = await self._staff_repo.update(updated)
            updated_staffs[updated.id] = updated

        return list(awards.values()), list(updated_player_stats.values()), list(updated_staffs.values())

    async def _get_or_create_award(
        self,
        item: PlayerAwardDict | ManagerAwardDict,
    ) -> AwardEntity | None:
        award_type_str = item["type"]
        try:
            award_type = AwardTypeEnum.from_string(award_type_str)
        except ValueError:
            return None

        source_id = AwardEntity.get_source_id(award_type)
        existing = await self._award_repo.get_by_pulselive_id(source_id)
        if existing is not None:
            return existing

        created = AwardEntity(_type=award_type)
        result = await self._award_repo.create(created)
        return result or await self._award_repo.get_by_pulselive_id(source_id)

    async def _get_player_stat_for_award(
        self,
        item: PlayerAwardDict,
        season: SeasonEntity,
    ) -> PlayerStatEntity | None:
        player = await self._player_repo.get_by_pulselive_id(item["id"])
        if player is None:
            return None
        return await self._player_stat_repo.get_by_player_season(player, season)

    async def _get_or_create_staff(self, item: ManagerAwardDict) -> StaffEntity | None:
        source_id = str(item["id"])
        existing = await self._staff_repo.get_by_pulselive_id(source_id)
        if existing is not None:
            return existing

        display_name_en = item["name"]["simpleName"]
        created = StaffEntity(
            display_name_en=display_name_en,
            display_name_kr=await self._translator.translate_word(display_name_en),
            full_name=item["name"]["fullName"],
            source_id=source_id,
        )
        result = await self._staff_repo.create(created)
        return result or await self._staff_repo.get_by_pulselive_id(source_id)

    @staticmethod
    def _parse_award_date(date_str: str) -> datetime | None:
        try:
            parts = date_str.split("-")
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2]) if len(parts) > 2 else 1
            return (
                datetime(year, month, day, tzinfo=UTC)
                .astimezone(UTC)
                .replace(tzinfo=None)
            )
        except (IndexError, ValueError):
            return None
