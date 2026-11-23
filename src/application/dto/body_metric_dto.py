from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class CreateBodyMetricDTO:
    recorded_at: date
    bodyweight: Optional[float] = None
    measurements: Optional[dict] = None
    notes: Optional[str] = None


@dataclass
class BodyMetricDTO:
    id: str
    recorded_at: date
    bodyweight: Optional[float]
    measurements: Optional[dict]
    notes: Optional[str]
