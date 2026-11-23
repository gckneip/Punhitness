from datetime import date, timedelta
from src.domain.entities.exercise import Exercise, MuscleGroup
from src.domain.entities.workout_session import WorkoutSession, SessionExercise, SetEntry
from src.domain.services.training_summary_service import TrainingSummaryService
from tests._fakes import FakeWorkoutSessionRepo, FakeExerciseRepo


def _session(session_date, exercise_id="bench", sets=None):
    sets = sets if sets is not None else [SetEntry(set_number=1, weight=100.0, reps=5)]
    return WorkoutSession(
        session_date=session_date,
        exercises=[SessionExercise(exercise_id=exercise_id, sets=sets)],
    )


TODAY = date(2026, 6, 15)


def _service(sessions, exercises=()):
    return TrainingSummaryService(FakeWorkoutSessionRepo(sessions), FakeExerciseRepo(exercises))


def test_sessions_count_and_frequency_within_window(monkeypatch):
    sessions = [_session(TODAY - timedelta(days=d)) for d in (1, 3, 5, 40)]
    svc = _service(sessions)
    _patch_today(monkeypatch, svc)
    summary = svc.get_summary(days=30)
    assert summary.sessions_count == 3  # the 40-day-old session falls outside the window
    assert summary.sessions_per_week == 3 / (30 / 7.0)


def test_total_volume_sums_weight_times_reps(monkeypatch):
    s = _session(TODAY, sets=[
        SetEntry(set_number=1, weight=100.0, reps=5),
        SetEntry(set_number=2, weight=100.0, reps=3),
    ])
    svc = _service([s])
    _patch_today(monkeypatch, svc)
    summary = svc.get_summary(days=30)
    assert summary.total_volume == 100.0 * 5 + 100.0 * 3


def test_muscle_group_distribution_counts_session_exercises(monkeypatch):
    bench = Exercise(name="Bench", muscle_group=MuscleGroup.CHEST)
    squat = Exercise(name="Squat", muscle_group=MuscleGroup.QUADS)
    sessions = [
        _session(TODAY, exercise_id=bench.id),
        _session(TODAY, exercise_id=bench.id),
        _session(TODAY, exercise_id=squat.id),
    ]
    svc = _service(sessions, exercises=[bench, squat])
    _patch_today(monkeypatch, svc)
    summary = svc.get_summary(days=30)
    assert summary.muscle_group_distribution == {"Chest": 2, "Quads": 1}


def test_muscle_group_distribution_is_empty_without_exercise_repo(monkeypatch):
    svc = TrainingSummaryService(FakeWorkoutSessionRepo([_session(TODAY)]))
    _patch_today(monkeypatch, svc)
    summary = svc.get_summary(days=30)
    assert summary.muscle_group_distribution == {}


def test_streak_breaks_on_a_gap(monkeypatch):
    sessions = [
        _session(TODAY),
        _session(TODAY - timedelta(days=1)),
        _session(TODAY - timedelta(days=2)),
        _session(TODAY - timedelta(days=4)),  # gap at day 3 breaks the streak
    ]
    svc = _service(sessions)
    _patch_today(monkeypatch, svc)
    summary = svc.get_summary(days=30)
    assert summary.current_streak_days == 3


def test_streak_is_zero_if_last_session_older_than_yesterday(monkeypatch):
    svc = _service([_session(TODAY - timedelta(days=2))])
    _patch_today(monkeypatch, svc)
    summary = svc.get_summary(days=30)
    assert summary.current_streak_days == 0


def _patch_today(monkeypatch, svc):
    import src.domain.services.training_summary_service as module
    monkeypatch.setattr(module, "date", _FixedToday)


class _FixedToday(date):
    @classmethod
    def today(cls):
        return TODAY
