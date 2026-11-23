import sqlite3
from datetime import date, datetime
from typing import List, Optional
from src.domain.entities.workout_session import WorkoutSession, SessionExercise, SetEntry
from src.domain.repositories.workout_session_repository import WorkoutSessionRepository


class SQLiteWorkoutSessionRepository(WorkoutSessionRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def save(self, session: WorkoutSession) -> None:
        existing = self._conn.execute(
            "SELECT created_at FROM workout_sessions WHERE id = ?", (session.id,)
        ).fetchone()
        created_at = existing["created_at"] if existing else datetime.now().isoformat()

        self._conn.execute(
            """INSERT OR REPLACE INTO workout_sessions
               (id, session_date, note, routine_id, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (session.id, session.session_date.isoformat(), session.note, session.routine_id, created_at),
        )

        old_exercise_ids = [
            r["id"] for r in self._conn.execute(
                "SELECT id FROM session_exercises WHERE session_id = ?", (session.id,)
            ).fetchall()
        ]
        for se_id in old_exercise_ids:
            self._conn.execute("DELETE FROM sets WHERE session_exercise_id = ?", (se_id,))
        self._conn.execute("DELETE FROM session_exercises WHERE session_id = ?", (session.id,))

        for session_exercise in session.exercises:
            self._conn.execute(
                """INSERT INTO session_exercises (id, session_id, exercise_id, sort_order)
                   VALUES (?, ?, ?, ?)""",
                (session_exercise.id, session.id, session_exercise.exercise_id, session_exercise.sort_order),
            )
            for set_entry in session_exercise.sets:
                self._conn.execute(
                    """INSERT INTO sets
                       (id, session_exercise_id, set_number, weight, reps, rpe, notes)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        set_entry.id, session_exercise.id, set_entry.set_number,
                        set_entry.weight, set_entry.reps, set_entry.rpe, set_entry.notes,
                    ),
                )
        self._conn.commit()

    def find_by_id(self, session_id: str) -> Optional[WorkoutSession]:
        row = self._conn.execute(
            "SELECT * FROM workout_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row is None:
            return None
        return self._row_to_session(row)

    def find_all(
        self,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        limit: Optional[int] = None,
    ) -> List[WorkoutSession]:
        query = "SELECT * FROM workout_sessions WHERE 1=1"
        params: list = []
        if date_from is not None:
            query += " AND session_date >= ?"
            params.append(date_from.isoformat())
        if date_to is not None:
            query += " AND session_date < ?"
            params.append(date_to.isoformat())
        query += " ORDER BY session_date DESC, created_at DESC"
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_session(row) for row in rows]

    def find_recent(self, limit: int = 10) -> List[WorkoutSession]:
        return self.find_all(limit=limit)

    def find_by_exercise(self, exercise_id: str, limit: Optional[int] = None) -> List[WorkoutSession]:
        query = """SELECT DISTINCT workout_sessions.* FROM workout_sessions
                   JOIN session_exercises ON session_exercises.session_id = workout_sessions.id
                   WHERE session_exercises.exercise_id = ?
                   ORDER BY workout_sessions.session_date DESC, workout_sessions.created_at DESC"""
        params: list = [exercise_id]
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
        rows = self._conn.execute(query, params).fetchall()
        return [self._row_to_session(row) for row in rows]

    def delete(self, session_id: str) -> None:
        exercise_ids = [
            r["id"] for r in self._conn.execute(
                "SELECT id FROM session_exercises WHERE session_id = ?", (session_id,)
            ).fetchall()
        ]
        for se_id in exercise_ids:
            self._conn.execute("DELETE FROM sets WHERE session_exercise_id = ?", (se_id,))
        self._conn.execute("DELETE FROM session_exercises WHERE session_id = ?", (session_id,))
        self._conn.execute("DELETE FROM workout_sessions WHERE id = ?", (session_id,))
        self._conn.commit()

    def _row_to_session(self, row: sqlite3.Row) -> WorkoutSession:
        exercise_rows = self._conn.execute(
            "SELECT * FROM session_exercises WHERE session_id = ? ORDER BY sort_order",
            (row["id"],),
        ).fetchall()
        exercises = []
        for ex_row in exercise_rows:
            set_rows = self._conn.execute(
                "SELECT * FROM sets WHERE session_exercise_id = ? ORDER BY set_number",
                (ex_row["id"],),
            ).fetchall()
            sets = [
                SetEntry(
                    id=s["id"], set_number=s["set_number"], weight=s["weight"],
                    reps=s["reps"], rpe=s["rpe"], notes=s["notes"],
                )
                for s in set_rows
            ]
            exercises.append(
                SessionExercise(
                    id=ex_row["id"], exercise_id=ex_row["exercise_id"],
                    sort_order=ex_row["sort_order"], sets=sets,
                )
            )
        return WorkoutSession(
            id=row["id"],
            session_date=date.fromisoformat(row["session_date"]),
            note=row["note"],
            routine_id=row["routine_id"],
            exercises=exercises,
        )
