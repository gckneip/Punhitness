from typing import List, Optional
from src.domain.entities.routine import Routine, RoutineExerciseSlot
from src.domain.repositories.routine_repository import RoutineRepository
from src.application.dto.routine_dto import CreateRoutineDTO, RoutineDTO, RoutineSlotDTO


class RoutineUseCases:
    def __init__(self, routine_repository: RoutineRepository):
        self._routine_repository = routine_repository

    def create_routine(self, dto: CreateRoutineDTO) -> RoutineDTO:
        routine = Routine(
            name=dto.name,
            notes=dto.notes,
            slots=[
                RoutineExerciseSlot(
                    exercise_id=s.exercise_id,
                    sort_order=s.sort_order,
                    target_sets=s.target_sets,
                    target_reps=s.target_reps,
                    target_weight=s.target_weight,
                )
                for s in dto.slots
            ],
        )
        self._routine_repository.save(routine)
        return self._to_dto(routine)

    def update_routine(self, routine_id: str, dto: CreateRoutineDTO) -> Optional[RoutineDTO]:
        routine = self._routine_repository.find_by_id(routine_id)
        if routine is None:
            return None
        routine.name = dto.name
        routine.notes = dto.notes
        routine.slots = [
            RoutineExerciseSlot(
                exercise_id=s.exercise_id,
                sort_order=s.sort_order,
                target_sets=s.target_sets,
                target_reps=s.target_reps,
                target_weight=s.target_weight,
            )
            for s in dto.slots
        ]
        self._routine_repository.save(routine)
        return self._to_dto(routine)

    def list_routines(self) -> List[RoutineDTO]:
        return [self._to_dto(r) for r in self._routine_repository.find_all()]

    def get_routine(self, routine_id: str) -> Optional[RoutineDTO]:
        routine = self._routine_repository.find_by_id(routine_id)
        return self._to_dto(routine) if routine else None

    def delete_routine(self, routine_id: str) -> None:
        self._routine_repository.delete(routine_id)

    def _to_dto(self, routine: Routine) -> RoutineDTO:
        return RoutineDTO(
            id=routine.id,
            name=routine.name,
            notes=routine.notes,
            slots=[
                RoutineSlotDTO(
                    id=s.id,
                    exercise_id=s.exercise_id,
                    sort_order=s.sort_order,
                    target_sets=s.target_sets,
                    target_reps=s.target_reps,
                    target_weight=s.target_weight,
                )
                for s in routine.slots
            ],
        )
