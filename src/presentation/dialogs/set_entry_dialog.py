from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox,
    QDialogButtonBox, QVBoxLayout, QMessageBox,
)


class SetEntryDialog(QDialog):
    def __init__(self, parent=None, set_entry=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Set" if set_entry else "Add Set")
        self.setModal(True)
        self.resize(300, 220)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0, 1000)
        self.weight_spin.setDecimals(1)
        self.weight_spin.setSuffix(" kg")
        form.addRow("Weight:", self.weight_spin)

        self.reps_spin = QSpinBox()
        self.reps_spin.setRange(0, 200)
        form.addRow("Reps:", self.reps_spin)

        self.rpe_spin = QDoubleSpinBox()
        self.rpe_spin.setRange(0, 10)
        self.rpe_spin.setDecimals(1)
        self.rpe_spin.setSpecialValueText("—")
        form.addRow("RPE:", self.rpe_spin)

        self.notes_edit = QLineEdit()
        form.addRow("Notes:", self.notes_edit)

        layout.addLayout(form)

        if set_entry is not None:
            self.weight_spin.setValue(set_entry.weight)
            self.reps_spin.setValue(set_entry.reps)
            self.rpe_spin.setValue(set_entry.rpe or 0.0)
            self.notes_edit.setText(set_entry.notes or "")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate_and_accept(self):
        if self.reps_spin.value() <= 0:
            QMessageBox.warning(self, "Warning", "Reps must be greater than zero.")
            return
        self.accept()

    def get_data(self):
        return {
            "weight": self.weight_spin.value(),
            "reps": self.reps_spin.value(),
            "rpe": self.rpe_spin.value() or None,
            "notes": self.notes_edit.text().strip() or None,
        }
