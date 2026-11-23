from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, Optional
from src.domain.repositories.workout_session_repository import WorkoutSessionRepository


@dataclass
class TrainingSummary:
    sessions_count: int
    sessions_per_week: float
    current_streak_days: int
    total_volume: float
    muscle_group_distribution: Dict[str, int] = field(default_factory=dict)


class TrainingSummaryService:
    def __init__(self, workout_session_repository: WorkoutSessionRepository, exercise_repository=None):
        self._workout_session_repository = workout_session_repository
        self._exercise_repository = exercise_repository

    def get_summary(self, days: int = 30) -> TrainingSummary:
        today = date.today()
        date_from = today - timedelta(days=days)
        sessions = self._workout_session_repository.find_all(
            date_from=date_from, date_to=today + timedelta(days=1)
        )

        sessions_count = len(sessions)
        sessions_per_week = sessions_count / max(days / 7.0, 1e-9)
        total_volume = sum(
            s.weight * s.reps
            for session in sessions
            for session_exercise in session.exercises
            for s in session_exercise.sets
        )

        muscle_group_distribution: Dict[str, int] = {}
        if self._exercise_repository is not None:
            muscle_cache: Dict[str, str] = {}
            for session in sessions:
                for session_exercise in session.exercises:
                    exercise_id = session_exercise.exercise_id
                    if exercise_id not in muscle_cache:
                        exercise = self._exercise_repository.find_by_id(exercise_id)
                        muscle_cache[exercise_id] = exercise.muscle_group.value if exercise else "Unknown"
                    muscle_group = muscle_cache[exercise_id]
                    muscle_group_distribution[muscle_group] = muscle_group_distribution.get(muscle_group, 0) + 1

        return TrainingSummary(
            sessions_count=sessions_count,
            sessions_per_week=sessions_per_week,
            current_streak_days=self._compute_streak(today),
            total_volume=total_volume,
            muscle_group_distribution=muscle_group_distribution,
        )

    def _compute_streak(self, today: date) -> int:
        all_sessions = self._workout_session_repository.find_all()
        session_dates = sorted({s.session_date for s in all_sessions}, reverse=True)
        if not session_dates or session_dates[0] not in (today, today - timedelta(days=1)):
            return 0
        streak = 1
        for i in range(1, len(session_dates)):
            if session_dates[i] == session_dates[i - 1] - timedelta(days=1):
                streak += 1
            else:
                break
        return streak
