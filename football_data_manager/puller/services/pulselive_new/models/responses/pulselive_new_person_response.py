from pydantic import Field, AliasChoices

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveNewPersonResponse(CamelCaseModel):
    first_name: str = Field(validation_alias=AliasChoices("first", "firstName"))
    last_name: str = Field(validation_alias=AliasChoices("last", "lastName"))
    display_name: str | None = Field(
        None, validation_alias=AliasChoices("display", "name", "knownName")
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def simple_name(self):
        return self.display_name or self.full_name
