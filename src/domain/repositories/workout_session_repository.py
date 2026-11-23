from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional
from src.domain.entities.workout_session import WorkoutSession


class WorkoutSessionRepository(ABC):
    @abstractmethod
    def save(self, session: WorkoutSession) -> None:
        """Persists the session and replaces all of its exercises/sets."""
        pass

    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional[WorkoutSession]:
        pass

    @abstractmethod
    def find_all(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: Optional[int] = None,
    ) -> List[WorkoutSession]:
        pass

    @abstractmethod
    def find_recent(self, limit: int = 10) -> List[WorkoutSession]:
        pass

    @abstractmethod
    def find_by_exercise(self, exercise_id: str, limit: Optional[int] = None) -> List[WorkoutSession]:
        """Sessions containing at least one SessionExercise for this exercise_id."""
        pass

    @abstractmethod
    def delete(self, session_id: str) -> None:
        pass
