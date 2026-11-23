import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class MuscleGroup(Enum):
    CHEST = "Chest"
    BACK = "Back"
    LEGS = "Legs"
    SHOULDERS = "Shoulders"
    ARMS = "Arms"
    CORE = "Core"
    CARDIO = "Cardio"
    FULL_BODY = "Full Body"


@dataclass
class Exercise:
    name: str
    muscle_group: MuscleGroup
    equipment: Optional[str] = None
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
