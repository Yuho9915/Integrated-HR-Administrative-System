from abc import ABC, abstractmethod
from typing import Any


class DatabaseAdapter(ABC):
    @abstractmethod
    def healthcheck(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def list_collection(self, resource: str) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def create_record(self, resource: str, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
