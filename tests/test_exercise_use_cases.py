from src.domain.entities.exercise import MuscleGroup
from src.application.dto.exercise_dto import CreateExerciseDTO
from src.application.use_cases.exercise_use_cases import ExerciseUseCases
from tests._fakes import FakeExerciseRepo


def _use_cases(exercises=()):
    return ExerciseUseCases(FakeExerciseRepo(exercises))


def test_create_exercise_round_trips_through_dto():
    uc = _use_cases()
    dto = uc.create_exercise(CreateExerciseDTO(name="Bench Press", muscle_group=MuscleGroup.CHEST, equipment="Barbell"))
    assert dto.name == "Bench Press"
    assert dto.muscle_group == "Chest"
    assert dto.equipment == "Barbell"
    assert uc.list_exercises() == [dto]


def test_update_exercise_changes_fields():
    uc = _use_cases()
    created = uc.create_exercise(CreateExerciseDTO(name="Squat", muscle_group=MuscleGroup.LEGS))
    updated = uc.update_exercise(
        created.id, CreateExerciseDTO(name="Back Squat", muscle_group=MuscleGroup.LEGS, notes="go deep")
    )
    assert updated.name == "Back Squat"
    assert updated.notes == "go deep"


def test_update_unknown_exercise_returns_none():
    uc = _use_cases()
    assert uc.update_exercise("missing", CreateExerciseDTO(name="X", muscle_group=MuscleGroup.CORE)) is None


def test_delete_exercise_removes_it_from_listing():
    uc = _use_cases()
    created = uc.create_exercise(CreateExerciseDTO(name="Deadlift", muscle_group=MuscleGroup.BACK))
    uc.delete_exercise(created.id)
    assert uc.list_exercises() == []
