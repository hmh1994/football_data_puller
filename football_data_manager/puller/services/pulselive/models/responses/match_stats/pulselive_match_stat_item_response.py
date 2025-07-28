from typing import Any

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)


class PulseliveMatchStatItemResponse(CamelCaseModel):
    name: str
    value: int | float
    description: str
    additional_info: dict[str, Any]
