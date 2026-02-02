from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

TResponse = TypeVar("TResponse", bound=BaseModel)


class AbstractPuller(ABC, Generic[TResponse]):
    """Abstract base class for all Pullers.

    Fetches data from external sources and returns Pydantic response models.
    Pullers only handle data collection; entity conversion is handled by Mergers.
    """

    @abstractmethod
    async def close(self) -> None:
        """Clean up client resources."""
        ...
