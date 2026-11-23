import sys
from PySide6.QtWidgets import QApplication, QMessageBox

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
from src.presentation import theme
from src.presentation.windows.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    try:
        conn = get_connection()
        create_tables(conn)
    except Exception as exc:
        QMessageBox.critical(None, "Database Error", f"Could not open the database:\n{exc}")
        sys.exit(1)

    app.setStyleSheet(theme.build_stylesheet())

    exercise_repo = SQLiteExerciseRepository(conn)
    routine_repo = SQLiteRoutineRepository(conn)
    workout_session_repo = SQLiteWorkoutSessionRepository(conn)
    body_metric_repo = SQLiteBodyMetricRepository(conn)

    exercise_use_cases = ExerciseUseCases(exercise_repo)
    routine_use_cases = RoutineUseCases(routine_repo)
    workout_session_use_cases = WorkoutSessionUseCases(workout_session_repo, routine_repo)
    body_metric_use_cases = BodyMetricUseCases(body_metric_repo)
    progress_service = ProgressService(workout_session_repo, exercise_repo)
    training_summary_service = TrainingSummaryService(workout_session_repo, exercise_repo)

    window = MainWindow(
        exercise_use_cases,
        routine_use_cases,
        workout_session_use_cases,
        body_metric_use_cases,
        progress_service,
        training_summary_service,
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
