import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MuscleGroup(Enum):
    CHEST = "Chest"
    LATS = "Lats"
    TRAPS = "Traps"
    LOWER_BACK = "Lower Back"
    FRONT_DELTS = "Front Delts"
    SIDE_DELTS = "Side Delts"
    REAR_DELTS = "Rear Delts"
    BICEPS = "Biceps"
    TRICEPS = "Triceps"
    FOREARMS = "Forearms"
    ABS = "Abs"
    OBLIQUES = "Obliques"
    QUADS = "Quads"
    HAMSTRINGS = "Hamstrings"
    GLUTES = "Glutes"
    CALVES = "Calves"
    CARDIO = "Cardio"
    FULL_BODY = "Full Body"


@dataclass
class Exercise:
    name: str
    muscle_group: MuscleGroup
    equipment: Optional[str] = None
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
