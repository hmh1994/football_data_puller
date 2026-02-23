from datetime import datetime

from football_data_manager.repository.entities.awards import AwardEntity
from football_data_manager.repository.entities.staff_award_association import (
    StaffAwardAssociation,
)
from football_data_manager.repository.entities.staffs import StaffEntity
from football_data_manager.repository.repositories.pulselive import (
    PulseliveRepository,
)
from football_data_manager.repository.session import SessionFactory


class StaffRepository(PulseliveRepository[StaffEntity]):
    """Repository for staff entities."""

    def __init__(self, session_factory: SessionFactory):
        super().__init__(session_factory, StaffEntity)

    async def load_award_associations(self, staff: StaffEntity) -> StaffEntity:
        """Load award associations for staff."""
        return await self._load_lazy_fields(
            staff,
            [StaffAwardAssociation.AWARD_COLLECTION_NAME],
        )

    async def get_by_display_name_en(self, name: str) -> StaffEntity | None:
        """Get staff by English display name."""
        return await self._get_one_by_field(display_name_en=name)

    async def append_award_association(
        self,
        staff: StaffEntity,
        award: AwardEntity,
        date: datetime,
    ) -> StaffEntity:
        """Append staff-award association if not already present."""
        merged = await self.load_award_associations(staff)
        exists = any(
            assoc.award_id == award.id and assoc.date == date
            for assoc in merged.award_associations
        )
        if not exists:
            merged.award_associations.append(
                StaffAwardAssociation(staff=merged, award=award, date=date)
            )
            merged.award_associations.sort(key=lambda assoc: assoc.date)
        return merged
