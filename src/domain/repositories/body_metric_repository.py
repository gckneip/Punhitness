from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.body_metric import BodyMetricEntry


class BodyMetricRepository(ABC):
    @abstractmethod
    def save(self, entry: BodyMetricEntry) -> None:
        pass

    @abstractmethod
    def find_by_id(self, entry_id: str) -> Optional[BodyMetricEntry]:
        pass

    @abstractmethod
    def find_all(self, limit: Optional[int] = None) -> List[BodyMetricEntry]:
        """Most-recent-first."""
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> None:
        pass
