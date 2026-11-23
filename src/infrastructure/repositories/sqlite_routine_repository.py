import sqlite3
from datetime import datetime
from typing import List, Optional
from src.domain.entities.routine import Routine, RoutineExerciseSlot
from src.domain.repositories.routine_repository import RoutineRepository


class SQLiteRoutineRepository(RoutineRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def save(self, routine: Routine) -> None:
        existing = self._conn.execute(
            "SELECT created_at FROM routines WHERE id = ?", (routine.id,)
        ).fetchone()
        created_at = existing["created_at"] if existing else datetime.now().isoformat()

        self._conn.execute(
            "INSERT OR REPLACE INTO routines (id, name, notes, created_at) VALUES (?, ?, ?, ?)",
            (routine.id, routine.name, routine.notes, created_at),
        )
        self._conn.execute(
            "DELETE FROM routine_exercise_slots WHERE routine_id = ?", (routine.id,)
        )
        for slot in routine.slots:
            self._conn.execute(
                """INSERT INTO routine_exercise_slots
                   (id, routine_id, exercise_id, sort_order, target_sets, target_reps, target_weight)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    slot.id, routine.id, slot.exercise_id, slot.sort_order,
                    slot.target_sets, slot.target_reps, slot.target_weight,
                ),
            )
        self._conn.commit()

    def find_by_id(self, routine_id: str) -> Optional[Routine]:
        row = self._conn.execute(
            "SELECT * FROM routines WHERE id = ?", (routine_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_routine(row)

    def find_all(self) -> List[Routine]:
        rows = self._conn.execute("SELECT * FROM routines ORDER BY name").fetchall()
        return [self._row_to_routine(row) for row in rows]

    def delete(self, routine_id: str) -> None:
        self._conn.execute(
            "DELETE FROM routine_exercise_slots WHERE routine_id = ?", (routine_id,)
        )
        self._conn.execute("DELETE FROM routines WHERE id = ?", (routine_id,))
        self._conn.commit()

    def _row_to_routine(self, row: sqlite3.Row) -> Routine:
        slot_rows = self._conn.execute(
            "SELECT * FROM routine_exercise_slots WHERE routine_id = ? ORDER BY sort_order",
            (row["id"],),
        ).fetchall()
        slots = [
            RoutineExerciseSlot(
                id=s["id"],
                exercise_id=s["exercise_id"],
                sort_order=s["sort_order"],
                target_sets=s["target_sets"],
                target_reps=s["target_reps"],
                target_weight=s["target_weight"],
            )
            for s in slot_rows
        ]
        return Routine(id=row["id"], name=row["name"], notes=row["notes"], slots=slots)
