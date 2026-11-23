from dataclasses import dataclass
from typing import Optional
from src.domain.entities.exercise import MuscleGroup


@dataclass
class CreateExerciseDTO:
    name: str
    muscle_group: MuscleGroup
    equipment: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class ExerciseDTO:
    id: str
    name: str
    muscle_group: str
    equipment: Optional[str]
    notes: Optional[str]
