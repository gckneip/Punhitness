"""Read-only MCP server exposing the gym-tracker training log to an AI client
(Claude Code, Claude Desktop, Codex, ...) for analysis/tips.

A third presentation-layer entrypoint alongside src/main.py — no Qt imports
anywhere in this file or its import chain, so it runs headless. It re-wires
the exact same infrastructure/application layers the Qt app uses; no
business logic is duplicated here.

Logging workouts happens in the Qt UI, not through this server: every tool
below is read-only on purpose.
"""
from mcp.server.mcpserver import MCPServer

from src.infrastructure.database.connection import get_connection
from src.infrastructure.database.schema import create_tables
from src.infrastructure.repositories.sqlite_exercise_repository import SQLiteExerciseRepository
from src.infrastructure.repositories.sqlite_routine_repository import SQLiteRoutineRepository
from src.infrastructure.repositories.sqlite_workout_session_repository import SQLiteWorkoutSessionRepository
from src.infrastructure.repositories.sqlite_body_metric_repository import SQLiteBodyMetricRepository
from src.application.use_cases.exercise_use_cases import ExerciseUseCases
from src.application.use_cases.routine_use_cases import RoutineUseCases
from src.application.use_cases.workout_session_use_cases import WorkoutSessionUseCases
from src.application.use_cases.body_metric_use_cases import BodyMetricUseCases
from src.domain.services.progress_service import ProgressService
from src.domain.services.training_summary_service import TrainingSummaryService

mcp_server = MCPServer("gym-tracker")


def _wire():
    conn = get_connection()
    create_tables(conn)
    exercise_repo = SQLiteExerciseRepository(conn)
    routine_repo = SQLiteRoutineRepository(conn)
    session_repo = SQLiteWorkoutSessionRepository(conn)
    metric_repo = SQLiteBodyMetricRepository(conn)
    return {
        "exercises": ExerciseUseCases(exercise_repo),
        "routines": RoutineUseCases(routine_repo),
        "sessions": WorkoutSessionUseCases(session_repo, routine_repo),
        "metrics": BodyMetricUseCases(metric_repo),
        "progress": ProgressService(session_repo, exercise_repo),
        "summary": TrainingSummaryService(session_repo, exercise_repo),
    }


_ctx = _wire()


def _session_to_dict(session) -> dict:
    return {
        "id": session.id,
        "session_date": session.session_date.isoformat(),
        "note": session.note,
        "routine_id": session.routine_id,
        "exercises": [
            {
                "exercise_id": session_exercise.exercise_id,
                "sets": [
                    {
                        "set_number": s.set_number, "weight": s.weight,
                        "reps": s.reps, "rpe": s.rpe, "notes": s.notes,
                    }
                    for s in session_exercise.sets
                ],
            }
            for session_exercise in session.exercises
        ],
    }


@mcp_server.tool()
def list_exercises() -> list[dict]:
    """Full exercise catalog (name, muscle group, equipment, notes)."""
    return [
        {
            "id": e.id, "name": e.name, "muscle_group": e.muscle_group,
            "equipment": e.equipment, "notes": e.notes,
        }
        for e in _ctx["exercises"].list_exercises()
    ]


@mcp_server.tool()
def list_routines() -> list[dict]:
    """All routines with their ordered exercise slots and targets."""
    return [
        {
            "id": r.id, "name": r.name, "notes": r.notes,
            "slots": [
                {
                    "exercise_id": s.exercise_id, "sort_order": s.sort_order,
                    "target_sets": s.target_sets, "target_reps": s.target_reps,
                    "target_weight": s.target_weight,
                }
                for s in r.slots
            ],
        }
        for r in _ctx["routines"].list_routines()
    ]


@mcp_server.tool()
def get_recent_sessions(limit: int = 10) -> list[dict]:
    """Last `limit` logged workout sessions, most-recent-first, with exercises/sets."""
    return [_session_to_dict(s) for s in _ctx["sessions"].list_recent_sessions(limit=limit)]


@mcp_server.tool()
def get_exercise_history(exercise_name: str, limit: int = 20) -> dict:
    """Chronological sets/weight/reps/estimated-1RM for one exercise, by name."""
    exercise = _ctx["exercises"].get_by_name(exercise_name)
    if exercise is None:
        return {"error": f"No exercise named '{exercise_name}' found."}
    points = _ctx["progress"].get_exercise_history(exercise.id, limit=limit)
    return {
        "exercise": exercise.name,
        "history": [
            {
                "session_date": p.session_date.isoformat(), "weight": p.weight,
                "reps": p.reps, "estimated_1rm": round(p.estimated_1rm, 1),
            }
            for p in points
        ],
    }


@mcp_server.tool()
def get_body_metrics(limit: int = 20) -> list[dict]:
    """Most-recent-first bodyweight (+ measurements) entries."""
    return [
        {
            "id": e.id, "recorded_at": e.recorded_at.isoformat(),
            "bodyweight": e.bodyweight, "measurements": e.measurements, "notes": e.notes,
        }
        for e in _ctx["metrics"].list_metrics(limit=limit)
    ]


@mcp_server.tool()
def get_training_summary(days: int = 30) -> dict:
    """Sessions/week, current streak, total volume, muscle-group distribution over the last `days` days."""
    summary = _ctx["summary"].get_summary(days=days)
    return {
        "sessions_count": summary.sessions_count,
        "sessions_per_week": round(summary.sessions_per_week, 2),
        "current_streak_days": summary.current_streak_days,
        "total_volume": summary.total_volume,
        "muscle_group_distribution": summary.muscle_group_distribution,
    }


if __name__ == "__main__":
    mcp_server.run(transport="stdio")
