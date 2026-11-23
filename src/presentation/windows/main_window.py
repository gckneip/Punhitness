from typing import Optional

from PySide6.QtCore import Qt, QDate, QEvent
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QPushButton, QComboBox, QDateEdit,
    QMessageBox, QAbstractItemView, QFileDialog, QToolButton,
)

from src.domain.entities.exercise import Exercise, MuscleGroup
from src.application.dto.exercise_dto import CreateExerciseDTO
from src.application.dto.routine_dto import CreateRoutineDTO, CreateRoutineSlotDTO
from src.application.dto.body_metric_dto import CreateBodyMetricDTO
from src.infrastructure.theming.theme_parser import ThemeParseError
from src.presentation import icons
from src.presentation.app_restart import restart_app
from src.presentation.i18n import current_language, t
from src.presentation.labels import exercise_name_label, muscle_group_label
from src.presentation.dialogs.exercise_dialog import ExerciseDialog
from src.presentation.dialogs.routine_dialog import RoutineDialog
from src.presentation.dialogs.body_metric_dialog import BodyMetricDialog
from src.presentation.dialogs.settings_dialog import SettingsDialog
from src.presentation.widgets.session_editor_widget import SessionEditorWidget
from src.presentation.widgets.progress_chart_widget import ProgressChartWidget
from src.presentation.widgets.bodyweight_chart_widget import BodyweightChartWidget
from src.presentation.widgets.stat_card import make_stat_card
from src.presentation.widgets.muscle_mannequin_widget import MuscleMannequinWidget


class MainWindow(QMainWindow):
    def __init__(
        self,
        exercise_use_cases,
        routine_use_cases,
        workout_session_use_cases,
        body_metric_use_cases,
        progress_service,
        training_summary_service,
        app_settings_use_cases,
        theme_use_cases,
    ):
        super().__init__()
        self._exercise_use_cases = exercise_use_cases
        self._routine_use_cases = routine_use_cases
        self._workout_session_use_cases = workout_session_use_cases
        self._body_metric_use_cases = body_metric_use_cases
        self._progress_service = progress_service
        self._training_summary_service = training_summary_service
        self._app_settings_use_cases = app_settings_use_cases
        self._theme_use_cases = theme_use_cases
        self._muscle_filter: Optional[MuscleGroup] = None

        self.setWindowTitle(t("app.title"))
        self.resize(1000, 700)
        self._build_ui()
        self._reload_everything()

    def _build_ui(self):
        self._tabs = QTabWidget()
        self.setCentralWidget(self._tabs)

        settings_btn = QToolButton()
        settings_btn.setIcon(icons.icon("fa6s.gear"))
        settings_btn.setToolTip(t("dialog.settings.title"))
        settings_btn.setAutoRaise(True)
        settings_btn.clicked.connect(self._open_settings)
        self._tabs.setCornerWidget(settings_btn, Qt.TopRightCorner)

        self._build_dashboard_tab()
        self._build_exercises_tab()
        self._build_routines_tab()
        self._build_log_session_tab()
        self._build_body_metrics_tab()

    def _reload_everything(self):
        exercises = self._refresh_exercises_table()
        self._progress_chart.set_exercise_catalog(exercises)
        self._session_editor.set_exercise_catalog(exercises)
        self._refresh_routines_table()
        self._refresh_routine_picker()
        self._refresh_history_table()
        self._refresh_body_metrics_table()
        self._refresh_dashboard()

    # ---- Dashboard ----------------------------------------------------

    def _build_dashboard_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        stats_row = QHBoxLayout()
        self._sessions_week_label = QLabel("0")
        stats_row.addWidget(make_stat_card(t("dashboard.stat.sessions_per_week"), self._sessions_week_label))
        self._streak_label = QLabel("0")
        stats_row.addWidget(make_stat_card(t("dashboard.stat.streak"), self._streak_label))
        self._last_bodyweight_label = QLabel("—")
        stats_row.addWidget(make_stat_card(t("dashboard.stat.last_bodyweight"), self._last_bodyweight_label))
        layout.addLayout(stats_row)

        muscles_row = QHBoxLayout()
        self._muscles_worked_widget = MuscleMannequinWidget(
            selectable=False, title=t("dashboard.muscles_worked", days=30), show_legend=True,
        )
        self._muscles_worked_widget.setFixedWidth(230)
        muscles_row.addWidget(self._muscles_worked_widget)

        charts_col = QVBoxLayout()
        self._progress_chart = ProgressChartWidget(self._progress_service)
        charts_col.addWidget(self._progress_chart)

        self._dashboard_bodyweight_chart = BodyweightChartWidget()
        charts_col.addWidget(self._dashboard_bodyweight_chart)
        muscles_row.addLayout(charts_col, 1)

        layout.addLayout(muscles_row)

        self._tabs.addTab(tab, t("tab.dashboard"))

    def _refresh_dashboard(self):
        summary = self._training_summary_service.get_summary(days=30)
        self._sessions_week_label.setText(f"{summary.sessions_per_week:.1f}")
        self._streak_label.setText(str(summary.current_streak_days))

        metrics = self._body_metric_use_cases.list_metrics(limit=1)
        if metrics and metrics[0].bodyweight is not None:
            self._last_bodyweight_label.setText(f"{metrics[0].bodyweight:g} kg")
        else:
            self._last_bodyweight_label.setText("—")

        self._dashboard_bodyweight_chart.set_entries(self._body_metric_use_cases.list_metrics())

        distribution = summary.muscle_group_distribution
        max_count = max(distribution.values()) if distribution else 0
        intensities, labels = {}, {}
        for group in MuscleGroup:
            count = distribution.get(group.value, 0)
            intensities[group] = (count / max_count) if max_count else 0.0
            labels[group] = t("dashboard.muscle_logged", count=count) if count else t("dashboard.muscle_no_activity")
        self._muscles_worked_widget.set_intensities(intensities, labels)

    # ---- Exercises ------------------------------------------------------

    def _build_exercises_tab(self):
        tab = QWidget()
        outer = QHBoxLayout(tab)

        self._exercise_mannequin = MuscleMannequinWidget(selectable=True, title=t("exercises.filter_by_muscle"))
        self._exercise_mannequin.muscle_clicked.connect(self._on_exercise_muscle_filter_changed)
        self._exercise_mannequin.setFixedWidth(230)
        outer.addWidget(self._exercise_mannequin)

        layout = QVBoxLayout()
        outer.addLayout(layout, 1)

        self._exercises_table = QTableWidget(0, 3)
        self._exercises_table.setAlternatingRowColors(True)
        self._exercises_table.setHorizontalHeaderLabels(
            [t("table.col.name"), t("table.col.muscle_group"), t("table.col.equipment")]
        )
        self._exercises_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._exercises_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._exercises_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._exercises_table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton(t("common.add"))
        add_btn.clicked.connect(self._add_exercise)
        btn_row.addWidget(add_btn)
        edit_btn = QPushButton(t("common.edit"))
        edit_btn.clicked.connect(self._edit_exercise)
        btn_row.addWidget(edit_btn)
        delete_btn = QPushButton(t("common.delete"))
        delete_btn.clicked.connect(self._delete_exercise)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._tabs.addTab(tab, t("tab.exercises"))

    def _on_exercise_muscle_filter_changed(self, group):
        self._muscle_filter = group
        self._refresh_exercises_table()

    def _refresh_exercises_table(self):
        exercises = self._exercise_use_cases.list_exercises()
        filtered = (
            [e for e in exercises if e.muscle_group == self._muscle_filter.value]
            if self._muscle_filter else exercises
        )
        self._exercises_table.setRowCount(len(filtered))
        for row, exercise in enumerate(filtered):
            name_item = QTableWidgetItem(exercise_name_label(exercise.name))
            name_item.setData(Qt.UserRole, exercise.id)
            self._exercises_table.setItem(row, 0, name_item)
            self._exercises_table.setItem(row, 1, QTableWidgetItem(muscle_group_label(exercise.muscle_group)))
            self._exercises_table.setItem(row, 2, QTableWidgetItem(exercise.equipment or ""))
        return exercises

    def _selected_exercise_id(self):
        row = self._exercises_table.currentRow()
        if row < 0:
            return None
        return self._exercises_table.item(row, 0).data(Qt.UserRole)

    def _add_exercise(self):
        dialog = ExerciseDialog(self)
        if dialog.exec():
            self._exercise_use_cases.create_exercise(CreateExerciseDTO(**dialog.get_data()))
            self._reload_everything()

    def _edit_exercise(self):
        exercise_id = self._selected_exercise_id()
        if exercise_id is None:
            return
        dto = next(e for e in self._exercise_use_cases.list_exercises() if e.id == exercise_id)
        # ExerciseDialog's combo compares against MuscleGroup enum members, so the
        # DTO's plain string value needs resolving back to the enum for pre-fill.
        entity = Exercise(
            id=dto.id, name=dto.name, muscle_group=MuscleGroup(dto.muscle_group),
            equipment=dto.equipment, notes=dto.notes,
        )
        dialog = ExerciseDialog(self, exercise=entity)
        if dialog.exec():
            self._exercise_use_cases.update_exercise(exercise_id, CreateExerciseDTO(**dialog.get_data()))
            self._reload_everything()

    def _delete_exercise(self):
        exercise_id = self._selected_exercise_id()
        if exercise_id is None:
            return
        if QMessageBox.question(
            self, t("mainwindow.msg.delete_exercise.title"), t("mainwindow.msg.delete_exercise.body")
        ) == QMessageBox.Yes:
            self._exercise_use_cases.delete_exercise(exercise_id)
            self._reload_everything()

    # ---- Routines -------------------------------------------------------

    def _build_routines_tab(self):
        tab = QWidget()
        outer = QHBoxLayout(tab)

        self._routine_mannequin = MuscleMannequinWidget(
            selectable=False, title=t("routines.targets_title"), show_legend=True,
        )
        self._routine_mannequin.setFixedWidth(230)
        outer.addWidget(self._routine_mannequin)

        layout = QVBoxLayout()
        outer.addLayout(layout, 1)

        self._routines_table = QTableWidget(0, 2)
        self._routines_table.setAlternatingRowColors(True)
        self._routines_table.setHorizontalHeaderLabels([t("table.col.name"), t("table.col.notes")])
        self._routines_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._routines_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._routines_table.horizontalHeader().setStretchLastSection(True)
        self._routines_table.setMouseTracking(True)
        self._routines_table.cellEntered.connect(self._on_routine_row_hovered)
        self._routines_table.viewport().installEventFilter(self)
        layout.addWidget(self._routines_table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton(t("common.add"))
        add_btn.clicked.connect(self._add_routine)
        btn_row.addWidget(add_btn)
        edit_btn = QPushButton(t("common.edit"))
        edit_btn.clicked.connect(self._edit_routine)
        btn_row.addWidget(edit_btn)
        delete_btn = QPushButton(t("common.delete"))
        delete_btn.clicked.connect(self._delete_routine)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._tabs.addTab(tab, t("tab.routines"))
        self._reset_routine_mannequin()

    def eventFilter(self, obj, event):
        if obj is self._routines_table.viewport() and event.type() == QEvent.Leave:
            self._reset_routine_mannequin()
        return super().eventFilter(obj, event)

    def _on_routine_row_hovered(self, row, _col):
        item = self._routines_table.item(row, 0)
        if item is None:
            return
        routine_id = item.data(Qt.UserRole)
        routine = self._routine_use_cases.get_routine(routine_id)
        if routine is None:
            return
        self._update_routine_mannequin(routine)

    def _reset_routine_mannequin(self):
        intensities = {group: 0.0 for group in MuscleGroup}
        labels = {group: t("routines.hover_hint") for group in MuscleGroup}
        self._routine_mannequin.set_intensities(intensities, labels)

    def _update_routine_mannequin(self, routine):
        exercises_by_id = {e.id: e for e in self._exercise_use_cases.list_exercises()}
        counts = {}
        for slot in routine.slots:
            exercise = exercises_by_id.get(slot.exercise_id)
            if exercise is None:
                continue
            group = MuscleGroup(exercise.muscle_group)
            counts[group] = counts.get(group, 0) + 1

        max_count = max(counts.values()) if counts else 0
        intensities, labels = {}, {}
        for group in MuscleGroup:
            count = counts.get(group, 0)
            intensities[group] = (count / max_count) if max_count else 0.0
            labels[group] = t("routines.exercise_count", count=count) if count else t("routines.not_targeted")
        self._routine_mannequin.set_intensities(intensities, labels)

    def _refresh_routines_table(self):
        routines = self._routine_use_cases.list_routines()
        self._routines_table.setRowCount(len(routines))
        for row, routine in enumerate(routines):
            name_item = QTableWidgetItem(routine.name)
            name_item.setData(Qt.UserRole, routine.id)
            self._routines_table.setItem(row, 0, name_item)
            self._routines_table.setItem(row, 1, QTableWidgetItem(routine.notes or ""))
        return routines

    def _selected_routine_id(self):
        row = self._routines_table.currentRow()
        if row < 0:
            return None
        return self._routines_table.item(row, 0).data(Qt.UserRole)

    def _routine_dto_to_create_dto(self, data):
        return CreateRoutineDTO(
            name=data["name"],
            notes=data["notes"],
            slots=[CreateRoutineSlotDTO(**slot) for slot in data["slots"]],
        )

    def _add_routine(self):
        exercises = self._exercise_use_cases.list_exercises()
        if not exercises:
            QMessageBox.warning(self, t("common.warning"), t("mainwindow.msg.need_exercise"))
            return
        dialog = RoutineDialog(self, exercises=exercises)
        if dialog.exec():
            self._routine_use_cases.create_routine(self._routine_dto_to_create_dto(dialog.get_data()))
            self._reload_everything()

    def _edit_routine(self):
        routine_id = self._selected_routine_id()
        if routine_id is None:
            return
        routine = self._routine_use_cases.get_routine(routine_id)
        exercises = self._exercise_use_cases.list_exercises()
        dialog = RoutineDialog(self, routine=routine, exercises=exercises)
        if dialog.exec():
            self._routine_use_cases.update_routine(routine_id, self._routine_dto_to_create_dto(dialog.get_data()))
            self._reload_everything()

    def _delete_routine(self):
        routine_id = self._selected_routine_id()
        if routine_id is None:
            return
        if QMessageBox.question(
            self, t("mainwindow.msg.delete_routine.title"), t("mainwindow.msg.delete_routine.body")
        ) == QMessageBox.Yes:
            self._routine_use_cases.delete_routine(routine_id)
            self._reload_everything()

    # ---- Log Session / History ------------------------------------------

    def _build_log_session_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        start_row = QHBoxLayout()
        self._start_date_edit = QDateEdit()
        self._start_date_edit.setCalendarPopup(True)
        self._start_date_edit.setDate(QDate.currentDate())
        start_row.addWidget(self._start_date_edit)

        self._routine_picker_combo = QComboBox()
        start_row.addWidget(self._routine_picker_combo)

        start_from_routine_btn = QPushButton(t("logsession.start_from_routine"))
        start_from_routine_btn.clicked.connect(self._start_from_routine)
        start_row.addWidget(start_from_routine_btn)

        start_blank_btn = QPushButton(t("logsession.start_blank"))
        start_blank_btn.clicked.connect(self._start_blank_session)
        start_row.addWidget(start_blank_btn)
        start_row.addStretch()
        layout.addLayout(start_row)

        self._session_editor = SessionEditorWidget(self._workout_session_use_cases)
        self._session_editor.session_saved.connect(self._on_session_saved)
        layout.addWidget(self._session_editor)

        self._history_table = QTableWidget(0, 3)
        self._history_table.setAlternatingRowColors(True)
        self._history_table.setHorizontalHeaderLabels(
            [t("table.col.date"), t("table.col.routine"), t("table.col.exercises")]
        )
        self._history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._history_table.horizontalHeader().setStretchLastSection(True)
        self._history_table.cellDoubleClicked.connect(self._open_history_session)
        layout.addWidget(self._history_table)

        self._tabs.addTab(tab, t("tab.log_session"))

    def _refresh_routine_picker(self):
        self._routine_picker_combo.clear()
        for routine in self._routine_use_cases.list_routines():
            self._routine_picker_combo.addItem(routine.name, routine.id)

    def _refresh_history_table(self):
        routine_names = {r.id: r.name for r in self._routine_use_cases.list_routines()}
        sessions = self._workout_session_use_cases.list_recent_sessions(limit=50)
        self._history_table.setRowCount(len(sessions))
        for row, session in enumerate(sessions):
            date_item = QTableWidgetItem(session.session_date.isoformat())
            date_item.setData(Qt.UserRole, session.id)
            self._history_table.setItem(row, 0, date_item)
            routine_name = routine_names.get(session.routine_id, "—") if session.routine_id else "—"
            self._history_table.setItem(row, 1, QTableWidgetItem(routine_name))
            self._history_table.setItem(row, 2, QTableWidgetItem(str(len(session.exercises))))

    def _load_session_into_editor(self, session_dto):
        self._session_editor.set_exercise_catalog(self._exercise_use_cases.list_exercises())
        self._session_editor.load_session(session_dto)

    def _start_from_routine(self):
        routine_id = self._routine_picker_combo.currentData()
        if routine_id is None:
            QMessageBox.warning(self, t("common.warning"), t("mainwindow.msg.need_routine"))
            return
        session = self._workout_session_use_cases.start_session_from_routine(
            routine_id, self._start_date_edit.date().toPython()
        )
        self._load_session_into_editor(session)
        self._refresh_history_table()

    def _start_blank_session(self):
        session = self._workout_session_use_cases.start_blank_session(
            self._start_date_edit.date().toPython()
        )
        self._load_session_into_editor(session)
        self._refresh_history_table()

    def _open_history_session(self, row, _col):
        session_id = self._history_table.item(row, 0).data(Qt.UserRole)
        session = self._workout_session_use_cases.get_session(session_id)
        if session:
            self._load_session_into_editor(session)

    def _on_session_saved(self):
        self._refresh_history_table()
        self._refresh_dashboard()

    # ---- Body Metrics ----------------------------------------------------

    def _build_body_metrics_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        self._body_metrics_table = QTableWidget(0, 3)
        self._body_metrics_table.setAlternatingRowColors(True)
        self._body_metrics_table.setHorizontalHeaderLabels(
            [t("table.col.date"), t("table.col.bodyweight"), t("table.col.notes")]
        )
        self._body_metrics_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._body_metrics_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._body_metrics_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._body_metrics_table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton(t("common.add"))
        add_btn.clicked.connect(self._add_body_metric)
        btn_row.addWidget(add_btn)
        edit_btn = QPushButton(t("common.edit"))
        edit_btn.clicked.connect(self._edit_body_metric)
        btn_row.addWidget(edit_btn)
        delete_btn = QPushButton(t("common.delete"))
        delete_btn.clicked.connect(self._delete_body_metric)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        self._body_metrics_chart = BodyweightChartWidget()
        layout.addWidget(self._body_metrics_chart)

        self._tabs.addTab(tab, t("tab.body_metrics"))

    def _refresh_body_metrics_table(self):
        entries = self._body_metric_use_cases.list_metrics()
        self._body_metrics_table.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            date_item = QTableWidgetItem(entry.recorded_at.isoformat())
            date_item.setData(Qt.UserRole, entry.id)
            self._body_metrics_table.setItem(row, 0, date_item)
            weight_text = f"{entry.bodyweight:g} kg" if entry.bodyweight is not None else ""
            self._body_metrics_table.setItem(row, 1, QTableWidgetItem(weight_text))
            self._body_metrics_table.setItem(row, 2, QTableWidgetItem(entry.notes or ""))
        self._body_metrics_chart.set_entries(entries)

    def _selected_body_metric_id(self):
        row = self._body_metrics_table.currentRow()
        if row < 0:
            return None
        return self._body_metrics_table.item(row, 0).data(Qt.UserRole)

    def _add_body_metric(self):
        dialog = BodyMetricDialog(self)
        if dialog.exec():
            self._body_metric_use_cases.log_metric(CreateBodyMetricDTO(**dialog.get_data()))
            self._reload_everything()

    def _edit_body_metric(self):
        entry_id = self._selected_body_metric_id()
        if entry_id is None:
            return
        entry = next(e for e in self._body_metric_use_cases.list_metrics() if e.id == entry_id)
        dialog = BodyMetricDialog(self, entry=entry)
        if dialog.exec():
            self._body_metric_use_cases.update_metric(entry_id, CreateBodyMetricDTO(**dialog.get_data()))
            self._reload_everything()

    def _delete_body_metric(self):
        entry_id = self._selected_body_metric_id()
        if entry_id is None:
            return
        if QMessageBox.question(
            self, t("mainwindow.msg.delete_entry.title"), t("mainwindow.msg.delete_entry.body")
        ) == QMessageBox.Yes:
            self._body_metric_use_cases.delete_metric(entry_id)
            self._reload_everything()

    # ---- Settings -------------------------------------------------------

    def _open_settings(self):
        current_theme_id = self._app_settings_use_cases.get_current_theme_id()
        current_font_size = self._app_settings_use_cases.get_base_font_size()
        current_language_code = current_language()
        available_themes = self._theme_use_cases.list_available_themes()

        dialog = SettingsDialog(
            current_theme_id, available_themes, current_font_size,
            current_language=current_language_code, parent=self,
        )
        dialog.import_theme_requested.connect(lambda: self._handle_theme_import(dialog))
        if not dialog.exec():
            return

        data = dialog.get_data()
        changed_language = data["language"] and data["language"] != current_language_code
        changed_theme = data["theme_id"] and data["theme_id"] != current_theme_id
        changed_font = data["base_font_size"] != current_font_size
        if not (changed_language or changed_theme or changed_font):
            return

        box = QMessageBox(self)
        box.setWindowTitle(t("settings.restart.title"))
        box.setText(t("settings.restart.body"))
        restart_button = box.addButton(t("settings.restart.restart_now"), QMessageBox.AcceptRole)
        box.addButton(t("settings.restart.discard"), QMessageBox.RejectRole)
        box.setDefaultButton(restart_button)
        box.exec()
        if box.clickedButton() is not restart_button:
            return

        if changed_language:
            self._app_settings_use_cases.set_language(data["language"])
        if changed_theme:
            self._app_settings_use_cases.set_current_theme_id(data["theme_id"])
        if changed_font:
            self._app_settings_use_cases.set_base_font_size(data["base_font_size"])
        restart_app()

    def _handle_theme_import(self, dialog):
        path, _ = QFileDialog.getOpenFileName(
            self, t("mainwindow.dialog.import_theme.title"), "", t("mainwindow.dialog.import_theme.filter")
        )
        if not path:
            return

        try:
            result = self._theme_use_cases.import_theme_file(path)
        except ThemeParseError as exc:
            QMessageBox.critical(
                self, t("mainwindow.msg.import_error.title"),
                t("mainwindow.msg.theme_import_error.body", error=exc),
            )
            return

        all_themes = self._theme_use_cases.list_available_themes()
        dialog.select_theme(result.theme_id, all_themes)

        message = t("mainwindow.msg.theme_imported.body", name=result.name)
        if result.warnings:
            message += (
                "\n\n" + t("mainwindow.msg.theme_imported.warnings", count=len(result.warnings))
                + "\n" + "\n".join(result.warnings)
            )
        QMessageBox.information(self, t("mainwindow.msg.theme_imported.title"), message)
