from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewPersonResponse(CamelCaseModel):
    first_name: str
    last_name: str
    name: str | None = None
    known_name: str | None = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def simple_name(self):
        return self.known_name or self.name or self.full_name
