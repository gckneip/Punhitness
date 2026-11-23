from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.routine import Routine


class RoutineRepository(ABC):
    @abstractmethod
    def save(self, routine: Routine) -> None:
        """Persists the routine and replaces all of its slots."""
        pass

    @abstractmethod
    def find_by_id(self, routine_id: str) -> Optional[Routine]:
        pass

    @abstractmethod
    def find_all(self) -> List[Routine]:
        pass

    @abstractmethod
    def delete(self, routine_id: str) -> None:
        pass
