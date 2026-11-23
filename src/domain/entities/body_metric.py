import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class BodyMetricEntry:
    recorded_at: date
    bodyweight: Optional[float] = None
    measurements: Optional[dict] = None
    notes: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
