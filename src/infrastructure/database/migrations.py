"""One-time data migrations for schema/enum changes that can't be expressed
as a plain CREATE TABLE statement.

Run these against the raw connection (plain SQL, no domain entities) before
any repository touches the affected rows — once a MuscleGroup member is
removed from the enum, reconstructing an Exercise from an old stored value
(e.g. MuscleGroup("Legs")) raises ValueError, so the rewrite has to happen
first.
"""

# Legs/Arms/Core were split into finer groups (see
# src/domain/entities/exercise.py). This is a frozen historical mapping of
# the *old* default catalog's exercise names to their new group, independent
# of src/application/exercise_presets.py (which keeps evolving) — a
# migration must always do the same thing, regardless of later preset edits.
_NAME_OVERRIDES = {
    "Squat": "Quads",
    "Leg Press": "Quads",
    "Walking Lunge": "Quads",
    "Leg Extension": "Quads",
    "Leg Curl": "Hamstrings",
    "Romanian Deadlift": "Hamstrings",
    "Calf Raise": "Calves",
    "Barbell Curl": "Biceps",
    "Dumbbell Curl": "Biceps",
    "Hammer Curl": "Biceps",
    "Tricep Pushdown": "Triceps",
    "Skull Crusher": "Triceps",
    "Close-Grip Bench Press": "Triceps",
    "Plank": "Abs",
    "Crunch": "Abs",
    "Hanging Leg Raise": "Abs",
    "Russian Twist": "Obliques",
    "Ab Wheel Rollout": "Abs",
    "Sit-Up": "Abs",
}
# Anything else saved under the old broad group (user-renamed or custom
# exercises) falls back to this subgroup rather than being left unreadable.
_FALLBACK = {"Legs": "Quads", "Arms": "Biceps", "Core": "Abs"}


def migrate_legacy_muscle_groups(conn) -> None:
    placeholders = ", ".join("?" for _ in _FALLBACK)
    cursor = conn.execute(
        f"SELECT id, name, muscle_group FROM exercises WHERE muscle_group IN ({placeholders})",
        tuple(_FALLBACK),
    )
    rows = cursor.fetchall()
    for row in rows:
        new_group = _NAME_OVERRIDES.get(row["name"], _FALLBACK[row["muscle_group"]])
        conn.execute("UPDATE exercises SET muscle_group = ? WHERE id = ?", (new_group, row["id"]))
    if rows:
        conn.commit()
