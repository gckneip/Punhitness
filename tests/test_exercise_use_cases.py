from src.domain.entities.exercise import MuscleGroup
from src.application.dto.exercise_dto import CreateExerciseDTO
from src.application.exercise_presets import DEFAULT_EXERCISES
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
    created = uc.create_exercise(CreateExerciseDTO(name="Squat", muscle_group=MuscleGroup.QUADS))
    updated = uc.update_exercise(
        created.id, CreateExerciseDTO(name="Back Squat", muscle_group=MuscleGroup.QUADS, notes="go deep")
    )
    assert updated.name == "Back Squat"
    assert updated.notes == "go deep"


def test_update_unknown_exercise_returns_none():
    uc = _use_cases()
    assert uc.update_exercise("missing", CreateExerciseDTO(name="X", muscle_group=MuscleGroup.ABS)) is None


def test_delete_exercise_removes_it_from_listing():
    uc = _use_cases()
    created = uc.create_exercise(CreateExerciseDTO(name="Deadlift", muscle_group=MuscleGroup.LOWER_BACK))
    uc.delete_exercise(created.id)
    assert uc.list_exercises() == []


def test_seed_default_exercises_populates_an_empty_catalog():
    uc = _use_cases()
    uc.seed_default_exercises_if_empty()
    exercises = uc.list_exercises()
    assert len(exercises) == len(DEFAULT_EXERCISES)
    muscle_groups = {e.muscle_group for e in exercises}
    assert muscle_groups == {mg.value for mg in MuscleGroup}


def test_seed_default_exercises_is_a_noop_if_catalog_is_not_empty():
    uc = _use_cases()
    uc.create_exercise(CreateExerciseDTO(name="My Custom Lift", muscle_group=MuscleGroup.ABS))
    uc.seed_default_exercises_if_empty()
    exercises = uc.list_exercises()
    assert len(exercises) == 1
    assert exercises[0].name == "My Custom Lift"
