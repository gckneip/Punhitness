from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CreateRoutineSlotDTO:
    exercise_id: str
    sort_order: int = 0
    target_sets: Optional[int] = None
    target_reps: Optional[int] = None
    target_weight: Optional[float] = None


@dataclass
class CreateRoutineDTO:
    name: str
    notes: Optional[str] = None
    slots: List[CreateRoutineSlotDTO] = field(default_factory=list)


@dataclass
class RoutineSlotDTO:
    id: str
    exercise_id: str
    sort_order: int
    target_sets: Optional[int]
    target_reps: Optional[int]
    target_weight: Optional[float]


@dataclass
class RoutineDTO:
    id: str
    name: str
    notes: Optional[str]
    slots: List[RoutineSlotDTO]
