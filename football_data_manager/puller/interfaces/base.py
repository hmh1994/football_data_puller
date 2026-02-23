from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """Base model that maps camelCase JSON fields to snake_case Python fields.

    Kept available for intermediate models in other modules (e.g. Phase 3 Merger).
    Not used by puller/interfaces.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        extra="ignore",
        populate_by_name=True,
        strict=True,
        str_strip_whitespace=True,
        use_enum_values=True,
        validate_assignment=True,
        validate_default=True,
    )


class RawResponseModel(BaseModel):
    """Base model for receiving external API responses.

    Uses snake_case field names with camelCase alias generation.
    Accepts both camelCase and snake_case JSON keys via populate_by_name.
    All external API response models in puller/interfaces inherit from this class.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        extra="ignore",
        populate_by_name=True,
        str_strip_whitespace=True,
    )
