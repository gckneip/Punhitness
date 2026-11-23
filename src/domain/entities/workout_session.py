import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class SetEntry:
    set_number: int
    weight: float = 0.0
    reps: int = 0
    rpe: Optional[float] = None
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class SessionExercise:
    exercise_id: str
    sort_order: int = 0
    sets: List[SetEntry] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class WorkoutSession:
    session_date: date
    note: Optional[str] = None
    routine_id: Optional[str] = None
    exercises: List[SessionExercise] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
