from PySide6.QtCore import Signal, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QDateEdit,
    QComboBox, QPushButton, QGroupBox, QTableWidget, QTableWidgetItem,
    QMessageBox,
)
from src.application.dto.workout_session_dto import (
    CreateWorkoutSessionDTO, CreateSessionExerciseDTO, CreateSetDTO,
)
from src.domain.entities.workout_session import SetEntry
from src.presentation.dialogs.set_entry_dialog import SetEntryDialog
from src.presentation.i18n import t
from src.presentation.labels import exercise_name_label


class _ExerciseBlock:
    """In-memory state for one exercise's sets within the editor, backing the
    read-only preview table (edits always go through SetEntryDialog, matching
    the rest of the app's dialog-based CRUD pattern)."""

    def __init__(self, exercise_id: str, exercise_name: str, sets=None):
        self.exercise_id = exercise_id
        self.exercise_name = exercise_name
        self.sets = list(sets or [])  # list of dicts: weight/reps/rpe/notes


class SessionEditorWidget(QWidget):
    session_saved = Signal()

    def __init__(self, session_use_cases, parent=None):
        super().__init__(parent)
        self._session_use_cases = session_use_cases
        self._session_id = None
        self._routine_id = None
        self._exercises = []  # ExerciseDTO catalog, set via set_exercise_catalog
        self._blocks: list[_ExerciseBlock] = []

        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        form.addRow(t("field.date"), self.date_edit)
        self.note_edit = QLineEdit()
        form.addRow(t("field.note"), self.note_edit)
        layout.addLayout(form)

        self._blocks_layout = QVBoxLayout()
        layout.addLayout(self._blocks_layout)

        add_exercise_row = QHBoxLayout()
        self.exercise_combo = QComboBox()
        add_exercise_row.addWidget(self.exercise_combo)
        add_exercise_btn = QPushButton(t("session.add_exercise"))
        add_exercise_btn.clicked.connect(self._add_exercise_block_from_combo)
        add_exercise_row.addWidget(add_exercise_btn)
        add_exercise_row.addStretch()
        layout.addLayout(add_exercise_row)

        layout.addStretch()

        save_btn = QPushButton(t("session.save"))
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self._save)
        layout.addWidget(save_btn)

    def set_exercise_catalog(self, exercises):
        self._exercises = list(exercises)
        self.exercise_combo.clear()
        for exercise in self._exercises:
            self.exercise_combo.addItem(exercise_name_label(exercise.name), exercise.id)

    def load_session(self, session_dto):
        self._session_id = session_dto.id
        self._routine_id = session_dto.routine_id
        qdate = QDate(session_dto.session_date.year, session_dto.session_date.month, session_dto.session_date.day)
        self.date_edit.setDate(qdate)
        self.note_edit.setText(session_dto.note or "")

        self._blocks = []
        names_by_id = {e.id: exercise_name_label(e.name) for e in self._exercises}
        for session_exercise in session_dto.exercises:
            block = _ExerciseBlock(
                exercise_id=session_exercise.exercise_id,
                exercise_name=names_by_id.get(session_exercise.exercise_id, t("session.unknown_exercise")),
                sets=[
                    {"weight": s.weight, "reps": s.reps, "rpe": s.rpe, "notes": s.notes}
                    for s in session_exercise.sets
                ],
            )
            self._blocks.append(block)
        self._rebuild_blocks_ui()

    def _add_exercise_block_from_combo(self):
        exercise_id = self.exercise_combo.currentData()
        if exercise_id is None:
            return
        if any(b.exercise_id == exercise_id for b in self._blocks):
            QMessageBox.warning(self, t("common.warning"), t("msg.exercise_already_added"))
            return
        self._blocks.append(_ExerciseBlock(exercise_id, self.exercise_combo.currentText()))
        self._rebuild_blocks_ui()

    def _rebuild_blocks_ui(self):
        while self._blocks_layout.count():
            item = self._blocks_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for block in self._blocks:
            group = QGroupBox(block.exercise_name)
            group_layout = QVBoxLayout(group)

            table = QTableWidget(len(block.sets), 5)
            table.setAlternatingRowColors(True)
            table.setHorizontalHeaderLabels([
                t("table.session_col.set"), t("table.session_col.weight"),
                t("table.session_col.reps"), t("table.session_col.rpe"), t("table.col.notes"),
            ])
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.horizontalHeader().setStretchLastSection(True)
            self._fill_sets_table(table, block.sets)
            table.cellDoubleClicked.connect(
                lambda row, _col, b=block, tbl=table: self._edit_set(b, tbl, row)
            )
            group_layout.addWidget(table)

            btn_row = QHBoxLayout()
            add_set_btn = QPushButton(t("session.add_set"))
            add_set_btn.clicked.connect(lambda _=False, b=block, tbl=table: self._add_set(b, tbl))
            btn_row.addWidget(add_set_btn)
            remove_set_btn = QPushButton(t("session.remove_selected_set"))
            remove_set_btn.clicked.connect(lambda _=False, b=block, tbl=table: self._remove_set(b, tbl))
            btn_row.addWidget(remove_set_btn)
            remove_exercise_btn = QPushButton(t("session.remove_exercise"))
            remove_exercise_btn.clicked.connect(lambda _=False, b=block: self._remove_block(b))
            btn_row.addWidget(remove_exercise_btn)
            btn_row.addStretch()
            group_layout.addLayout(btn_row)

            self._blocks_layout.addWidget(group)

    def _fill_sets_table(self, table, sets):
        table.setRowCount(len(sets))
        for row, set_data in enumerate(sets):
            table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            table.setItem(row, 1, QTableWidgetItem(f"{set_data['weight']:g}"))
            table.setItem(row, 2, QTableWidgetItem(str(set_data["reps"])))
            table.setItem(row, 3, QTableWidgetItem(f"{set_data['rpe']:g}" if set_data.get("rpe") else ""))
            table.setItem(row, 4, QTableWidgetItem(set_data.get("notes") or ""))

    def _add_set(self, block: _ExerciseBlock, table: QTableWidget):
        dialog = SetEntryDialog(self)
        if dialog.exec():
            block.sets.append(dialog.get_data())
            self._fill_sets_table(table, block.sets)

    def _edit_set(self, block: _ExerciseBlock, table: QTableWidget, row: int):
        existing = block.sets[row]
        set_entry = SetEntry(
            set_number=row + 1, weight=existing["weight"], reps=existing["reps"],
            rpe=existing.get("rpe"), notes=existing.get("notes"),
        )
        dialog = SetEntryDialog(self, set_entry=set_entry)
        if dialog.exec():
            block.sets[row] = dialog.get_data()
            self._fill_sets_table(table, block.sets)

    def _remove_set(self, block: _ExerciseBlock, table: QTableWidget):
        row = table.currentRow()
        if row >= 0:
            block.sets.pop(row)
            self._fill_sets_table(table, block.sets)

    def _remove_block(self, block: _ExerciseBlock):
        self._blocks.remove(block)
        self._rebuild_blocks_ui()

    def _save(self):
        if self._session_id is None:
            return
        qdate = self.date_edit.date()
        dto = CreateWorkoutSessionDTO(
            session_date=qdate.toPython(),
            note=self.note_edit.text().strip() or None,
            routine_id=self._routine_id,
            exercises=[
                CreateSessionExerciseDTO(
                    exercise_id=block.exercise_id,
                    sort_order=index,
                    sets=[
                        CreateSetDTO(
                            set_number=set_index + 1, weight=s["weight"], reps=s["reps"],
                            rpe=s.get("rpe"), notes=s.get("notes"),
                        )
                        for set_index, s in enumerate(block.sets)
                    ],
                )
                for index, block in enumerate(self._blocks)
            ],
        )
        self._session_use_cases.save_session(self._session_id, dto)
        self.session_saved.emit()
