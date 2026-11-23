from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QVBoxLayout, QMessageBox,
)
from src.domain.entities.exercise import MuscleGroup


class ExerciseDialog(QDialog):
    def __init__(self, parent=None, exercise=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Exercise" if exercise else "New Exercise")
        self.setModal(True)
        self.resize(350, 220)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        form.addRow("Name:", self.name_edit)

        self.muscle_group_combo = QComboBox()
        for muscle_group in MuscleGroup:
            self.muscle_group_combo.addItem(muscle_group.value, muscle_group)
        form.addRow("Muscle group:", self.muscle_group_combo)

        self.equipment_edit = QLineEdit()
        form.addRow("Equipment:", self.equipment_edit)

        self.notes_edit = QLineEdit()
        form.addRow("Notes:", self.notes_edit)

        layout.addLayout(form)

        if exercise is not None:
            self.name_edit.setText(exercise.name)
            index = self.muscle_group_combo.findData(exercise.muscle_group)
            if index >= 0:
                self.muscle_group_combo.setCurrentIndex(index)
            self.equipment_edit.setText(exercise.equipment or "")
            self.notes_edit.setText(exercise.notes or "")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate_and_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Warning", "Name is required.")
            return
        self.accept()

    def get_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "muscle_group": self.muscle_group_combo.currentData(),
            "equipment": self.equipment_edit.text().strip() or None,
            "notes": self.notes_edit.text().strip() or None,
        }
