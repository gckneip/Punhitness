from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class CreateSetDTO:
    set_number: int
    weight: float = 0.0
    reps: int = 0
    rpe: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class CreateSessionExerciseDTO:
    exercise_id: str
    sort_order: int = 0
    sets: List[CreateSetDTO] = field(default_factory=list)


@dataclass
class CreateWorkoutSessionDTO:
    session_date: date
    note: Optional[str] = None
    routine_id: Optional[str] = None
    exercises: List[CreateSessionExerciseDTO] = field(default_factory=list)


@dataclass
class SetDTO:
    id: str
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float]
    notes: Optional[str]


@dataclass
class SessionExerciseDTO:
    id: str
    exercise_id: str
    sort_order: int
    sets: List[SetDTO]


@dataclass
class WorkoutSessionDTO:
    id: str
    session_date: date
    note: Optional[str]
    routine_id: Optional[str]
    exercises: List[SessionExerciseDTO]
