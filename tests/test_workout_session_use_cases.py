from datetime import date
from src.application.dto.routine_dto import CreateRoutineDTO, CreateRoutineSlotDTO
from src.application.dto.workout_session_dto import (
    CreateWorkoutSessionDTO, CreateSessionExerciseDTO, CreateSetDTO,
)
from src.application.use_cases.routine_use_cases import RoutineUseCases
from src.application.use_cases.workout_session_use_cases import WorkoutSessionUseCases
from tests._fakes import FakeRoutineRepo, FakeWorkoutSessionRepo


def _use_cases():
    routine_repo = FakeRoutineRepo()
    session_repo = FakeWorkoutSessionRepo()
    return (
        WorkoutSessionUseCases(session_repo, routine_repo),
        RoutineUseCases(routine_repo),
    )


def test_start_session_from_routine_carries_over_targets():
    session_uc, routine_uc = _use_cases()
    routine = routine_uc.create_routine(CreateRoutineDTO(
        name="Push Day",
        slots=[CreateRoutineSlotDTO(exercise_id="bench", sort_order=0, target_sets=3, target_reps=8, target_weight=60.0)],
    ))
    session = session_uc.start_session_from_routine(routine.id, date(2026, 2, 1))
    assert session.routine_id == routine.id
    assert len(session.exercises) == 1
    assert len(session.exercises[0].sets) == 3
    assert all(s.weight == 60.0 and s.reps == 8 for s in session.exercises[0].sets)


def test_start_session_from_unknown_routine_returns_none():
    session_uc, _ = _use_cases()
    assert session_uc.start_session_from_routine("missing", date(2026, 2, 1)) is None


def test_start_blank_session_has_no_exercises():
    session_uc, _ = _use_cases()
    session = session_uc.start_blank_session(date(2026, 2, 1))
    assert session.exercises == []
    assert session.routine_id is None


def test_save_session_replaces_exercises_and_sets():
    session_uc, _ = _use_cases()
    session = session_uc.start_blank_session(date(2026, 2, 1))
    updated = session_uc.save_session(session.id, CreateWorkoutSessionDTO(
        session_date=date(2026, 2, 1),
        exercises=[
            CreateSessionExerciseDTO(exercise_id="bench", sort_order=0, sets=[
                CreateSetDTO(set_number=1, weight=80.0, reps=5),
            ]),
        ],
    ))
    assert len(updated.exercises) == 1
    assert updated.exercises[0].sets[0].weight == 80.0

    # A second save with fewer exercises fully replaces the first one (no leftovers).
    replaced = session_uc.save_session(session.id, CreateWorkoutSessionDTO(
        session_date=date(2026, 2, 1), exercises=[],
    ))
    assert replaced.exercises == []


def test_list_recent_sessions_and_get_session():
    session_uc, _ = _use_cases()
    session_uc.start_blank_session(date(2026, 1, 1))
    second = session_uc.start_blank_session(date(2026, 1, 5))
    recent = session_uc.list_recent_sessions(limit=10)
    assert recent[0].id == second.id  # most recent first
    assert session_uc.get_session(second.id).session_date == date(2026, 1, 5)
    assert session_uc.get_session("missing") is None


def test_delete_session_removes_it():
    session_uc, _ = _use_cases()
    session = session_uc.start_blank_session(date(2026, 1, 1))
    session_uc.delete_session(session.id)
    assert session_uc.get_session(session.id) is None
