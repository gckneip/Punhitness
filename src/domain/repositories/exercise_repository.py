from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities.exercise import Exercise


class ExerciseRepository(ABC):
    @abstractmethod
    def save(self, exercise: Exercise) -> None:
        pass

    @abstractmethod
    def find_by_id(self, exercise_id: str) -> Optional[Exercise]:
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Exercise]:
        pass

    @abstractmethod
    def find_all(self) -> List[Exercise]:
        pass

    @abstractmethod
    def delete(self, exercise_id: str) -> None:
        pass
