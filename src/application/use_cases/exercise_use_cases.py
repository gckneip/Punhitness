from typing import List, Optional
from src.domain.entities.exercise import Exercise
from src.domain.repositories.exercise_repository import ExerciseRepository
from src.application.dto.exercise_dto import CreateExerciseDTO, ExerciseDTO


class ExerciseUseCases:
    def __init__(self, exercise_repository: ExerciseRepository):
        self._exercise_repository = exercise_repository

    def create_exercise(self, dto: CreateExerciseDTO) -> ExerciseDTO:
        exercise = Exercise(
            name=dto.name,
            muscle_group=dto.muscle_group,
            equipment=dto.equipment,
            notes=dto.notes,
        )
        self._exercise_repository.save(exercise)
        return self._to_dto(exercise)

    def update_exercise(self, exercise_id: str, dto: CreateExerciseDTO) -> Optional[ExerciseDTO]:
        exercise = self._exercise_repository.find_by_id(exercise_id)
        if exercise is None:
            return None
        exercise.name = dto.name
        exercise.muscle_group = dto.muscle_group
        exercise.equipment = dto.equipment
        exercise.notes = dto.notes
        self._exercise_repository.save(exercise)
        return self._to_dto(exercise)

    def list_exercises(self) -> List[ExerciseDTO]:
        return [self._to_dto(e) for e in self._exercise_repository.find_all()]

    def get_by_name(self, name: str) -> Optional[ExerciseDTO]:
        exercise = self._exercise_repository.find_by_name(name)
        return self._to_dto(exercise) if exercise else None

    def delete_exercise(self, exercise_id: str) -> None:
        self._exercise_repository.delete(exercise_id)

    def _to_dto(self, exercise: Exercise) -> ExerciseDTO:
        return ExerciseDTO(
            id=exercise.id,
            name=exercise.name,
            muscle_group=exercise.muscle_group.value,
            equipment=exercise.equipment,
            notes=exercise.notes,
        )
