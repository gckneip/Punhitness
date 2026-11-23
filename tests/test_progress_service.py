from datetime import date
from src.domain.entities.workout_session import WorkoutSession, SessionExercise, SetEntry
from src.domain.services.progress_service import ProgressService
from tests._fakes import FakeWorkoutSessionRepo, FakeExerciseRepo


def _session(session_date, exercise_id, sets):
    return WorkoutSession(
        session_date=session_date,
        exercises=[SessionExercise(exercise_id=exercise_id, sets=sets)],
    )


def _service(sessions):
    return ProgressService(FakeWorkoutSessionRepo(sessions), FakeExerciseRepo())


def test_estimated_1rm_uses_epley_formula():
    s = _session(date(2026, 1, 1), "bench", [SetEntry(set_number=1, weight=100.0, reps=5)])
    svc = _service([s])
    points = svc.get_exercise_history("bench")
    assert len(points) == 1
    assert points[0].estimated_1rm == 100.0 * (1 + 5 / 30)


def test_history_is_ordered_chronologically_and_filtered_by_exercise():
    s1 = _session(date(2026, 1, 10), "bench", [SetEntry(set_number=1, weight=100.0, reps=5)])
    s2 = _session(date(2026, 1, 1), "bench", [SetEntry(set_number=1, weight=90.0, reps=5)])
    s3 = _session(date(2026, 1, 5), "squat", [SetEntry(set_number=1, weight=150.0, reps=5)])
    svc = _service([s1, s2, s3])
    points = svc.get_exercise_history("bench")
    assert [p.session_date for p in points] == [date(2026, 1, 1), date(2026, 1, 10)]


def test_history_limit_keeps_most_recent_points():
    sessions = [
        _session(date(2026, 1, d), "bench", [SetEntry(set_number=1, weight=100.0, reps=5)])
        for d in range(1, 6)
    ]
    svc = _service(sessions)
    points = svc.get_exercise_history("bench", limit=2)
    assert [p.session_date for p in points] == [date(2026, 1, 4), date(2026, 1, 5)]


def test_best_set_picks_highest_estimated_1rm():
    s1 = _session(date(2026, 1, 1), "bench", [SetEntry(set_number=1, weight=100.0, reps=5)])
    s2 = _session(date(2026, 1, 2), "bench", [SetEntry(set_number=1, weight=120.0, reps=3)])
    svc = _service([s1, s2])
    best = svc.get_best_set("bench")
    assert best.weight == 120.0


def test_best_set_is_none_without_history():
    svc = _service([])
    assert svc.get_best_set("bench") is None


def test_volume_trend_grouped_by_session():
    s1 = _session(date(2026, 1, 1), "bench", [
        SetEntry(set_number=1, weight=100.0, reps=5),
        SetEntry(set_number=2, weight=100.0, reps=5),
    ])
    svc = _service([s1])
    points = svc.get_volume_trend(exercise_id="bench", group_by="session")
    assert len(points) == 1
    assert points[0].volume == 1000.0  # 2 sets * 100 * 5


def test_volume_trend_grouped_by_week_buckets_same_iso_week():
    s1 = _session(date(2026, 1, 5), "bench", [SetEntry(set_number=1, weight=100.0, reps=5)])  # ISO week 2, Mon
    s2 = _session(date(2026, 1, 7), "bench", [SetEntry(set_number=1, weight=100.0, reps=5)])  # ISO week 2, Wed
    svc = _service([s1, s2])
    points = svc.get_volume_trend(exercise_id="bench", group_by="week")
    assert len(points) == 1
    assert points[0].volume == 1000.0
