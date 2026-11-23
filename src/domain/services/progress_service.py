from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from src.domain.repositories.workout_session_repository import WorkoutSessionRepository
from src.domain.repositories.exercise_repository import ExerciseRepository


@dataclass
class ExerciseHistoryPoint:
    session_date: date
    weight: float
    reps: int
    estimated_1rm: float


@dataclass
class VolumePoint:
    period_start: date
    volume: float


class ProgressService:
    def __init__(
        self,
        workout_session_repository: WorkoutSessionRepository,
        exercise_repository: ExerciseRepository,
    ):
        self._workout_session_repository = workout_session_repository
        self._exercise_repository = exercise_repository

    def get_exercise_history(self, exercise_id: str, limit: Optional[int] = None) -> List[ExerciseHistoryPoint]:
        points = []
        for session in self._workout_session_repository.find_by_exercise(exercise_id):
            for session_exercise in session.exercises:
                if session_exercise.exercise_id != exercise_id:
                    continue
                for set_entry in session_exercise.sets:
                    # Epley formula: a quick, standard estimate of one-rep max.
                    estimated_1rm = set_entry.weight * (1 + set_entry.reps / 30)
                    points.append(
                        ExerciseHistoryPoint(
                            session_date=session.session_date,
                            weight=set_entry.weight,
                            reps=set_entry.reps,
                            estimated_1rm=estimated_1rm,
                        )
                    )
        points.sort(key=lambda p: p.session_date)
        if limit is not None:
            points = points[-limit:]
        return points

    def get_best_set(self, exercise_id: str) -> Optional[ExerciseHistoryPoint]:
        points = self.get_exercise_history(exercise_id)
        if not points:
            return None
        return max(points, key=lambda p: p.estimated_1rm)

    def get_volume_trend(self, exercise_id: Optional[str] = None, group_by: str = "week") -> List[VolumePoint]:
        if exercise_id is not None:
            sessions = self._workout_session_repository.find_by_exercise(exercise_id)
        else:
            sessions = self._workout_session_repository.find_all()

        session_volumes = []
        for session in sessions:
            volume = 0.0
            for session_exercise in session.exercises:
                if exercise_id is not None and session_exercise.exercise_id != exercise_id:
                    continue
                volume += sum(s.weight * s.reps for s in session_exercise.sets)
            session_volumes.append((session.session_date, volume))

        if group_by == "session":
            points = [VolumePoint(period_start=d, volume=v) for d, v in session_volumes]
        else:
            buckets = {}
            for d, v in session_volumes:
                year, week, _ = d.isocalendar()
                bucket_start = date.fromisocalendar(year, week, 1)
                buckets[bucket_start] = buckets.get(bucket_start, 0.0) + v
            points = [VolumePoint(period_start=k, volume=v) for k, v in buckets.items()]

        points.sort(key=lambda p: p.period_start)
        return points
