from datetime import datetime

from football_data_manager.common.repositories.awards.award_entity import (
    AwardEntity,
)
from football_data_manager.common.repositories.pulselive_repository import (
    PulseliveRepository,
)
from football_data_manager.common.repositories.staffs.staff_award_association import (
    StaffAwardAssociation,
)
from football_data_manager.common.repositories.staffs.staff_entity import (
    StaffEntity,
)
from football_data_manager.common.services.db.db_service import DbService


class StaffRepository(PulseliveRepository[StaffEntity]):
    """
    Repository for managing staff entities with multilingual name support.

    Provides specialized functionality for football coaching staff and management personnel
    including display name lookups in multiple languages and full name searches.
    Extends PulseliveRepository for standard PULSELIVE source operations.
    """

    def __init__(self, db_service: DbService):
        """
        Initialize the staff repository.

        :param db_service: Database service for database operations
        """
        super().__init__(db_service, StaffEntity)

    async def load_award_associations(self, staff: StaffEntity) -> StaffEntity:
        """
        Load award associations for the given staff entity.

        Uses lazy loading to fetch the award associations with the staff entity.
        This method must be called before accessing award_associations to ensure
        the relationships are loaded from the database.

        :param staff: Staff entity to load award associations for
        :returns: Staff entity with award associations loaded
        """
        return await self._load_lazy_fields(staff, ["award_associations"])

    async def append_award_association(
        self, staff: StaffEntity, award: AwardEntity, date: datetime
    ) -> StaffEntity:
        """
        Append an award association to the staff if it doesn't already exist.

        Uses efficient set-based duplicate checking with O(1) lookup performance.
        Automatically loads award associations and maintains chronological ordering by date.

        :param staff: Staff entity to update
        :param award: Award entity to associate
        :param date: Date when the award was given
        :returns: Updated staff entity with award association added if not duplicate
        """
        merged_staff = await self.load_award_associations(staff)

        # Efficient set-based duplicate checking with composite key (award_id, date) - O(1) lookup
        existing_awards = {
            (association.award_id, association.date)
            for association in merged_staff.award_associations
        }

        if (award.id, date) not in existing_awards:
            association = StaffAwardAssociation(
                staff=merged_staff, award=award, date=date
            )
            merged_staff.award_associations.append(association)
            merged_staff.award_associations.sort(key=lambda s: s.date)

        return merged_staff

    async def read_by_display_name_en(self, name: str) -> StaffEntity | None:
        """
        Read a staff entity by their English display name.

        Searches for a staff member using their English display name which serves
        as a unique identifier in the system.

        :param name: The English display name of the staff member
        :returns: The staff entity if found, otherwise None
        """
        return await self._read_one_by_field(display_name_en=name)

    async def read_by_full_name(self, name: str) -> StaffEntity | None:
        """
        Read a staff entity by their full legal name.

        Searches for a staff member using their complete legal name as recorded
        in the system.

        :param name: The full legal name of the staff member
        :returns: The staff entity if found, otherwise None
        """
        return await self._read_one_by_field(full_name=name)
