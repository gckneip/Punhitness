from datetime import date
from typing import List, Optional
from src.domain.entities.workout_session import WorkoutSession, SessionExercise, SetEntry
from src.domain.repositories.workout_session_repository import WorkoutSessionRepository
from src.domain.repositories.routine_repository import RoutineRepository
from src.application.dto.workout_session_dto import (
    CreateWorkoutSessionDTO, WorkoutSessionDTO, SessionExerciseDTO, SetDTO,
)


class WorkoutSessionUseCases:
    def __init__(
        self,
        workout_session_repository: WorkoutSessionRepository,
        routine_repository: RoutineRepository,
    ):
        self._workout_session_repository = workout_session_repository
        self._routine_repository = routine_repository

    def start_session_from_routine(self, routine_id: str, session_date: date) -> Optional[WorkoutSessionDTO]:
        routine = self._routine_repository.find_by_id(routine_id)
        if routine is None:
            return None
        exercises = []
        for slot in sorted(routine.slots, key=lambda s: s.sort_order):
            sets = []
            if slot.target_sets:
                for set_number in range(1, slot.target_sets + 1):
                    sets.append(
                        SetEntry(
                            set_number=set_number,
                            weight=slot.target_weight or 0.0,
                            reps=slot.target_reps or 0,
                        )
                    )
            exercises.append(
                SessionExercise(exercise_id=slot.exercise_id, sort_order=slot.sort_order, sets=sets)
            )
        session = WorkoutSession(session_date=session_date, routine_id=routine.id, exercises=exercises)
        self._workout_session_repository.save(session)
        return self._to_dto(session)

    def start_blank_session(self, session_date: date) -> WorkoutSessionDTO:
        session = WorkoutSession(session_date=session_date)
        self._workout_session_repository.save(session)
        return self._to_dto(session)

    def save_session(self, session_id: str, dto: CreateWorkoutSessionDTO) -> Optional[WorkoutSessionDTO]:
        session = self._workout_session_repository.find_by_id(session_id)
        if session is None:
            return None
        session.session_date = dto.session_date
        session.note = dto.note
        session.routine_id = dto.routine_id
        session.exercises = [
            SessionExercise(
                exercise_id=se.exercise_id,
                sort_order=se.sort_order,
                sets=[
                    SetEntry(
                        set_number=s.set_number, weight=s.weight, reps=s.reps,
                        rpe=s.rpe, notes=s.notes,
                    )
                    for s in se.sets
                ],
            )
            for se in dto.exercises
        ]
        self._workout_session_repository.save(session)
        return self._to_dto(session)

    def list_recent_sessions(self, limit: int = 20) -> List[WorkoutSessionDTO]:
        return [self._to_dto(s) for s in self._workout_session_repository.find_recent(limit=limit)]

    def get_session(self, session_id: str) -> Optional[WorkoutSessionDTO]:
        session = self._workout_session_repository.find_by_id(session_id)
        return self._to_dto(session) if session else None

    def delete_session(self, session_id: str) -> None:
        self._workout_session_repository.delete(session_id)

    def _to_dto(self, session: WorkoutSession) -> WorkoutSessionDTO:
        return WorkoutSessionDTO(
            id=session.id,
            session_date=session.session_date,
            note=session.note,
            routine_id=session.routine_id,
            exercises=[
                SessionExerciseDTO(
                    id=se.id,
                    exercise_id=se.exercise_id,
                    sort_order=se.sort_order,
                    sets=[
                        SetDTO(
                            id=s.id, set_number=s.set_number, weight=s.weight,
                            reps=s.reps, rpe=s.rpe, notes=s.notes,
                        )
                        for s in se.sets
                    ],
                )
                for se in session.exercises
            ],
        )
