from football_data_manager.merger.services.translator import TranslatorService
from football_data_manager.puller.interfaces.pulselive.v1_competition import (
    V1CompetitionResponse,
)
from football_data_manager.repository.entities.competitions import CompetitionEntity
from football_data_manager.repository.repositories.competitions import (
    CompetitionRepository,
)


class CompetitionMerger:
    """Merge Pulselive competition response into competition entities."""

    ALLOWED_IDS = ["1", "2", "5", "6", "8", "1007", "1125"]

    def __init__(
        self,
        competition_repo: CompetitionRepository,
        translator: TranslatorService,
    ):
        self._competition_repo = competition_repo
        self._translator = translator

    async def merge(self, response: V1CompetitionResponse) -> list[CompetitionEntity]:
        """Upsert allowed competitions from API response."""
        results: list[CompetitionEntity] = []

        for item in response.data:
            source_id = str(item["id"])
            if source_id not in self.ALLOWED_IDS:
                continue

            existing = await self._competition_repo.get_by_pulselive_id(source_id)
            if existing is not None:
                results.append(existing)
                continue

            name_en = item["name"]
            name_kr = await self._translator.translate_word(name_en)
            entity = CompetitionEntity(
                abbreviation=item["code"],
                name_en=name_en,
                name_kr=name_kr,
                source_id=source_id,
            )
            created = await self._competition_repo.create(entity)
            if created is not None:
                results.append(created)

        return results
