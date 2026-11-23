from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QDialogButtonBox, QVBoxLayout, QHBoxLayout, QMessageBox,
    QTableWidget, QPushButton,
)
from src.presentation.i18n import t


class RoutineDialog(QDialog):
    """`exercises` is the full ExerciseDTO catalog, used to populate each
    slot row's exercise picker."""

    def __init__(self, parent=None, routine=None, exercises=()):
        super().__init__(parent)
        self._exercises = list(exercises)
        columns = [t("table.col.exercise"), t("table.routine_col.sets"),
                   t("table.routine_col.reps"), t("table.routine_col.weight")]
        self.setWindowTitle(t("dialog.routine.edit_title") if routine else t("dialog.routine.new_title"))
        self.setModal(True)
        self.resize(480, 420)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        form.addRow(t("field.name"), self.name_edit)

        self.notes_edit = QLineEdit()
        form.addRow(t("field.notes"), self.notes_edit)

        layout.addLayout(form)

        self.table = QTableWidget(0, len(columns))
        self.table.setAlternatingRowColors(True)
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        row_buttons = QHBoxLayout()
        add_btn = QPushButton(t("routine.add_slot"))
        add_btn.clicked.connect(lambda: self._add_row())
        remove_btn = QPushButton(t("routine.remove_selected"))
        remove_btn.clicked.connect(self._remove_selected_row)
        up_btn = QPushButton(t("routine.move_up"))
        up_btn.clicked.connect(lambda: self._move_selected_row(-1))
        down_btn = QPushButton(t("routine.move_down"))
        down_btn.clicked.connect(lambda: self._move_selected_row(1))
        for btn in (add_btn, remove_btn, up_btn, down_btn):
            row_buttons.addWidget(btn)
        layout.addLayout(row_buttons)

        if routine is not None:
            self.name_edit.setText(routine.name)
            self.notes_edit.setText(routine.notes or "")
            for slot in routine.slots:
                self._add_row(slot)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _add_row(self, slot=None):
        row = self.table.rowCount()
        self.table.insertRow(row)

        exercise_combo = QComboBox()
        for exercise in self._exercises:
            exercise_combo.addItem(exercise.name, exercise.id)
        if slot is not None:
            index = exercise_combo.findData(slot.exercise_id)
            if index >= 0:
                exercise_combo.setCurrentIndex(index)
        self.table.setCellWidget(row, 0, exercise_combo)

        sets_spin = QSpinBox()
        sets_spin.setRange(0, 20)
        sets_spin.setValue(slot.target_sets if slot and slot.target_sets else 3)
        self.table.setCellWidget(row, 1, sets_spin)

        reps_spin = QSpinBox()
        reps_spin.setRange(0, 100)
        reps_spin.setValue(slot.target_reps if slot and slot.target_reps else 10)
        self.table.setCellWidget(row, 2, reps_spin)

        weight_spin = QDoubleSpinBox()
        weight_spin.setRange(0, 1000)
        weight_spin.setDecimals(1)
        weight_spin.setValue(slot.target_weight if slot and slot.target_weight else 0.0)
        self.table.setCellWidget(row, 3, weight_spin)

    def _remove_selected_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)

    def _move_selected_row(self, direction: int):
        row = self.table.currentRow()
        target = row + direction
        if row < 0 or target < 0 or target >= self.table.rowCount():
            return
        for col in range(self.table.columnCount()):
            widget_a = self.table.cellWidget(row, col)
            widget_b = self.table.cellWidget(target, col)
            self.table.setCellWidget(row, col, widget_b)
            self.table.setCellWidget(target, col, widget_a)
        self.table.setCurrentCell(target, 0)

    def _validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, t("common.warning"), t("msg.name_required"))
            return
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, t("common.warning"), t("msg.add_one_slot"))
            return
        for row in range(self.table.rowCount()):
            combo = self.table.cellWidget(row, 0)
            if combo is None or combo.currentData() is None:
                QMessageBox.warning(self, t("common.warning"), t("msg.slot_needs_exercise"))
                return
        self.accept()

    def get_data(self):
        slots = []
        for row in range(self.table.rowCount()):
            exercise_combo = self.table.cellWidget(row, 0)
            sets_spin = self.table.cellWidget(row, 1)
            reps_spin = self.table.cellWidget(row, 2)
            weight_spin = self.table.cellWidget(row, 3)
            slots.append({
                "exercise_id": exercise_combo.currentData(),
                "sort_order": row,
                "target_sets": sets_spin.value() or None,
                "target_reps": reps_spin.value() or None,
                "target_weight": weight_spin.value() or None,
            })
        return {
            "name": self.name_edit.text().strip(),
            "notes": self.notes_edit.text().strip() or None,
            "slots": slots,
        }
