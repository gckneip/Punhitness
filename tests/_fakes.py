"""Lightweight in-memory fake repositories for pure service/use-case unit tests.

These keep tests focused on business logic (no SQLite setup). Only the
methods the services/use cases actually call are implemented.
"""
from typing import Optional


class FakeExerciseRepo:
    def __init__(self, exercises=()):
        self._exercises = {e.id: e for e in exercises}

    def save(self, exercise):
        self._exercises[exercise.id] = exercise

    def find_by_id(self, exercise_id):
        return self._exercises.get(exercise_id)

    def find_by_name(self, name):
        for e in self._exercises.values():
            if e.name.lower() == name.lower():
                return e
        return None

    def find_all(self):
        return list(self._exercises.values())

    def delete(self, exercise_id):
        self._exercises.pop(exercise_id, None)


class FakeRoutineRepo:
    def __init__(self, routines=()):
        self._routines = {r.id: r for r in routines}

    def save(self, routine):
        self._routines[routine.id] = routine

    def find_by_id(self, routine_id):
        return self._routines.get(routine_id)

    def find_all(self):
        return list(self._routines.values())

    def delete(self, routine_id):
        self._routines.pop(routine_id, None)


class FakeWorkoutSessionRepo:
    def __init__(self, sessions=()):
        self._sessions = {s.id: s for s in sessions}

    def save(self, session):
        self._sessions[session.id] = session

    def find_by_id(self, session_id):
        return self._sessions.get(session_id)

    def find_all(self, date_from=None, date_to=None, limit: Optional[int] = None):
        res = list(self._sessions.values())
        if date_from is not None:
            res = [s for s in res if s.session_date >= date_from]
        if date_to is not None:
            res = [s for s in res if s.session_date < date_to]
        res.sort(key=lambda s: s.session_date, reverse=True)
        if limit is not None:
            res = res[:limit]
        return res

    def find_recent(self, limit: int = 10):
        return self.find_all(limit=limit)

    def find_by_exercise(self, exercise_id, limit: Optional[int] = None):
        res = [
            s for s in self._sessions.values()
            if any(se.exercise_id == exercise_id for se in s.exercises)
        ]
        res.sort(key=lambda s: s.session_date, reverse=True)
        if limit is not None:
            res = res[:limit]
        return res

    def delete(self, session_id):
        self._sessions.pop(session_id, None)


class FakeBodyMetricRepo:
    def __init__(self, entries=()):
        self._entries = {e.id: e for e in entries}

    def save(self, entry):
        self._entries[entry.id] = entry

    def find_by_id(self, entry_id):
        return self._entries.get(entry_id)

    def find_all(self, limit: Optional[int] = None):
        res = sorted(self._entries.values(), key=lambda e: e.recorded_at, reverse=True)
        if limit is not None:
            res = res[:limit]
        return res

    def delete(self, entry_id):
        self._entries.pop(entry_id, None)
