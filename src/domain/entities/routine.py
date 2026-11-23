import uuid
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RoutineExerciseSlot:
    exercise_id: str
    sort_order: int = 0
    target_sets: Optional[int] = None
    target_reps: Optional[int] = None
    target_weight: Optional[float] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Routine:
    name: str
    notes: Optional[str] = None
    slots: List[RoutineExerciseSlot] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
