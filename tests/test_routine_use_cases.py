from src.application.dto.routine_dto import CreateRoutineDTO, CreateRoutineSlotDTO
from src.application.use_cases.routine_use_cases import RoutineUseCases
from tests._fakes import FakeRoutineRepo


def _use_cases():
    return RoutineUseCases(FakeRoutineRepo())


def test_create_routine_persists_ordered_slots():
    uc = _use_cases()
    dto = uc.create_routine(CreateRoutineDTO(
        name="Push Day",
        slots=[
            CreateRoutineSlotDTO(exercise_id="bench", sort_order=0, target_sets=3, target_reps=8, target_weight=60.0),
            CreateRoutineSlotDTO(exercise_id="ohp", sort_order=1, target_sets=3, target_reps=10),
        ],
    ))
    assert dto.name == "Push Day"
    assert [s.exercise_id for s in dto.slots] == ["bench", "ohp"]
    assert dto.slots[0].target_weight == 60.0


def test_update_routine_replaces_slots():
    uc = _use_cases()
    created = uc.create_routine(CreateRoutineDTO(
        name="Push Day", slots=[CreateRoutineSlotDTO(exercise_id="bench", sort_order=0)],
    ))
    updated = uc.update_routine(created.id, CreateRoutineDTO(
        name="Push Day v2", slots=[CreateRoutineSlotDTO(exercise_id="ohp", sort_order=0)],
    ))
    assert updated.name == "Push Day v2"
    assert [s.exercise_id for s in updated.slots] == ["ohp"]


def test_get_routine_and_list_routines():
    uc = _use_cases()
    created = uc.create_routine(CreateRoutineDTO(name="Leg Day", slots=[]))
    assert uc.get_routine(created.id).name == "Leg Day"
    assert uc.get_routine("missing") is None
    assert len(uc.list_routines()) == 1


def test_delete_routine_removes_it():
    uc = _use_cases()
    created = uc.create_routine(CreateRoutineDTO(name="Pull Day", slots=[]))
    uc.delete_routine(created.id)
    assert uc.list_routines() == []
