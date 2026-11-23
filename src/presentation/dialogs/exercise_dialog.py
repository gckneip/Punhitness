from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QVBoxLayout, QMessageBox,
)
from src.presentation.i18n import t
from src.presentation.labels import muscle_group_choices


class ExerciseDialog(QDialog):
    def __init__(self, parent=None, exercise=None):
        super().__init__(parent)
        self.setWindowTitle(t("dialog.exercise.edit_title") if exercise else t("dialog.exercise.new_title"))
        self.setModal(True)
        self.resize(350, 220)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit()
        form.addRow(t("field.name"), self.name_edit)

        self.muscle_group_combo = QComboBox()
        for muscle_group, label in muscle_group_choices():
            self.muscle_group_combo.addItem(label, muscle_group)
        form.addRow(t("field.muscle_group"), self.muscle_group_combo)

        self.equipment_edit = QLineEdit()
        form.addRow(t("field.equipment"), self.equipment_edit)

        self.notes_edit = QLineEdit()
        form.addRow(t("field.notes"), self.notes_edit)

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
            QMessageBox.warning(self, t("common.warning"), t("msg.name_required"))
            return
        self.accept()

    def get_data(self):
        return {
            "name": self.name_edit.text().strip(),
            "muscle_group": self.muscle_group_combo.currentData(),
            "equipment": self.equipment_edit.text().strip() or None,
            "notes": self.notes_edit.text().strip() or None,
        }
