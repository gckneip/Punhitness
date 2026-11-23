import sqlite3
from typing import List, Optional
from src.domain.entities.exercise import Exercise, MuscleGroup
from src.domain.repositories.exercise_repository import ExerciseRepository


class SQLiteExerciseRepository(ExerciseRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def save(self, exercise: Exercise) -> None:
        self._conn.execute(
            """INSERT OR REPLACE INTO exercises (id, name, muscle_group, equipment, notes)
               VALUES (?, ?, ?, ?, ?)""",
            (exercise.id, exercise.name, exercise.muscle_group.value, exercise.equipment, exercise.notes),
        )
        self._conn.commit()

    def find_by_id(self, exercise_id: str) -> Optional[Exercise]:
        cursor = self._conn.execute(
            "SELECT id, name, muscle_group, equipment, notes FROM exercises WHERE id = ?",
            (exercise_id,),
        )
        row = cursor.fetchone()
        return self._row_to_exercise(row) if row else None

    def find_by_name(self, name: str) -> Optional[Exercise]:
        cursor = self._conn.execute(
            "SELECT id, name, muscle_group, equipment, notes FROM exercises WHERE name = ? COLLATE NOCASE",
            (name,),
        )
        row = cursor.fetchone()
        return self._row_to_exercise(row) if row else None

    def find_all(self) -> List[Exercise]:
        cursor = self._conn.execute(
            "SELECT id, name, muscle_group, equipment, notes FROM exercises ORDER BY name"
        )
        return [self._row_to_exercise(row) for row in cursor.fetchall()]

    def delete(self, exercise_id: str) -> None:
        self._conn.execute("DELETE FROM exercises WHERE id = ?", (exercise_id,))
        self._conn.commit()

    def _row_to_exercise(self, row: sqlite3.Row) -> Exercise:
        return Exercise(
            id=row["id"],
            name=row["name"],
            muscle_group=MuscleGroup(row["muscle_group"]),
            equipment=row["equipment"],
            notes=row["notes"],
        )
