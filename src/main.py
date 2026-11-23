import sys
from PySide6.QtWidgets import QApplication, QMessageBox

from src.infrastructure.config.settings import THEMES_DIR
from src.infrastructure.database.connection import get_connection
from src.infrastructure.database.schema import create_tables
from src.infrastructure.repositories.sqlite_exercise_repository import SQLiteExerciseRepository
from src.infrastructure.repositories.sqlite_routine_repository import SQLiteRoutineRepository
from src.infrastructure.repositories.sqlite_workout_session_repository import SQLiteWorkoutSessionRepository
from src.infrastructure.repositories.sqlite_body_metric_repository import SQLiteBodyMetricRepository
from src.infrastructure.repositories.sqlite_app_settings_repository import SQLiteAppSettingsRepository
from src.infrastructure.theming.theme_file_repository import FileThemeRepository
from src.application.use_cases.exercise_use_cases import ExerciseUseCases
from src.application.use_cases.routine_use_cases import RoutineUseCases
from src.application.use_cases.workout_session_use_cases import WorkoutSessionUseCases
from src.application.use_cases.body_metric_use_cases import BodyMetricUseCases
from src.application.use_cases.app_settings_use_cases import AppSettingsUseCases
from src.application.use_cases.theme_use_cases import ThemeUseCases
from src.domain.entities.theme import LIGHT_PALETTE
from src.domain.services.progress_service import ProgressService
from src.domain.services.training_summary_service import TrainingSummaryService
from src.presentation import theme
from src.presentation import i18n
from src.presentation.i18n import t
from src.presentation.windows.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    try:
        conn = get_connection()
        create_tables(conn)
    except Exception as exc:
        QMessageBox.critical(None, "Database Error", f"Could not open the database:\n{exc}")
        sys.exit(1)

    app_settings_repo = SQLiteAppSettingsRepository(conn)
    app_settings_use_cases = AppSettingsUseCases(app_settings_repo)
    theme_repo = FileThemeRepository(THEMES_DIR)
    theme_use_cases = ThemeUseCases(theme_repo)

    language = app_settings_use_cases.get_language()
    if language is None:
        language = i18n.detect_default_language()
        app_settings_use_cases.set_language(language)
    i18n.load_language(language)

    theme_id = app_settings_use_cases.get_current_theme_id()
    palette = theme_use_cases.resolve_palette(theme_id)
    fallback_notice = None
    if palette is None:
        fallback_notice = t("msg.theme_fallback", theme_id=theme_id)
        app_settings_use_cases.set_current_theme_id("builtin:light")
        palette = LIGHT_PALETTE

    theme.load_palette(palette)
    theme.load_font_size(app_settings_use_cases.get_base_font_size())
    app.setStyleSheet(theme.build_stylesheet())
    theme.configure_pyqtgraph_theme()
    if fallback_notice:
        QMessageBox.warning(None, t("msg.theme_not_found.title"), fallback_notice)

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
        app_settings_use_cases,
        theme_use_cases,
    )
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
