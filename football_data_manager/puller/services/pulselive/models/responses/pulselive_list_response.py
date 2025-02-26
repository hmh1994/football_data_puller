from typing import TypeVar, Generic

from pydantic import RootModel

from football_data_manager.common.utils.pydantic_helper.camelcase_model import (
    CamelCaseModel,
)

TResponse = TypeVar("TResponse", bound=CamelCaseModel)


class PulseliveListResponse(RootModel[list[TResponse]], Generic[TResponse]):
    root: list[TResponse]
