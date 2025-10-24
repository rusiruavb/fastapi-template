from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseClient(ABC, Generic[T]):
    """Base interface for clients."""

    def __init__(self):
        self.client: T = None

    @abstractmethod
    def get_client(self) -> T:
        pass
