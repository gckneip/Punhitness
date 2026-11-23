def create_tables(conn):
    conn.executescript("""
        PRAGMA foreign_keys=OFF;

        CREATE TABLE IF NOT EXISTS exercises (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            muscle_group TEXT NOT NULL,
            equipment TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS routines (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            notes TEXT,
            created_at TEXT
        );

        CREATE TABLE IF NOT EXISTS routine_exercise_slots (
            id TEXT PRIMARY KEY,
            routine_id TEXT NOT NULL,
            exercise_id TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            target_sets INTEGER,
            target_reps INTEGER,
            target_weight REAL,
            FOREIGN KEY(routine_id) REFERENCES routines(id),
            FOREIGN KEY(exercise_id) REFERENCES exercises(id)
        );

        CREATE TABLE IF NOT EXISTS workout_sessions (
            id TEXT PRIMARY KEY,
            session_date TEXT NOT NULL,
            note TEXT,
            routine_id TEXT,
            created_at TEXT,
            FOREIGN KEY(routine_id) REFERENCES routines(id)
        );

        CREATE TABLE IF NOT EXISTS session_exercises (
            id TEXT PRIMARY KEY,
            session_id TEXT NOT NULL,
            exercise_id TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(session_id) REFERENCES workout_sessions(id),
            FOREIGN KEY(exercise_id) REFERENCES exercises(id)
        );

        CREATE TABLE IF NOT EXISTS sets (
            id TEXT PRIMARY KEY,
            session_exercise_id TEXT NOT NULL,
            set_number INTEGER NOT NULL,
            weight REAL NOT NULL DEFAULT 0,
            reps INTEGER NOT NULL DEFAULT 0,
            rpe REAL,
            notes TEXT,
            FOREIGN KEY(session_exercise_id) REFERENCES session_exercises(id)
        );

        CREATE TABLE IF NOT EXISTS body_metrics (
            id TEXT PRIMARY KEY,
            recorded_at TEXT NOT NULL,
            bodyweight REAL,
            measurements_json TEXT,
            notes TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_routine_exercise_slots_routine_id ON routine_exercise_slots(routine_id);
        CREATE INDEX IF NOT EXISTS idx_workout_sessions_session_date ON workout_sessions(session_date);
        CREATE INDEX IF NOT EXISTS idx_session_exercises_session_id ON session_exercises(session_id);
        CREATE INDEX IF NOT EXISTS idx_session_exercises_exercise_id ON session_exercises(exercise_id);
        CREATE INDEX IF NOT EXISTS idx_sets_session_exercise_id ON sets(session_exercise_id);
        CREATE INDEX IF NOT EXISTS idx_body_metrics_recorded_at ON body_metrics(recorded_at);

        PRAGMA foreign_keys=ON;
    """)
    conn.commit()
