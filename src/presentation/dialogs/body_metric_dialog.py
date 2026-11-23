from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QDateEdit,
    QDialogButtonBox, QVBoxLayout, QMessageBox,
)
from PySide6.QtCore import QDate


class BodyMetricDialog(QDialog):
    def __init__(self, parent=None, entry=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Body Metric" if entry else "Log Body Metric")
        self.setModal(True)
        self.resize(320, 200)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form.addRow("Date:", self.date_edit)

        self.bodyweight_spin = QDoubleSpinBox()
        self.bodyweight_spin.setRange(0, 500)
        self.bodyweight_spin.setDecimals(1)
        self.bodyweight_spin.setSuffix(" kg")
        form.addRow("Bodyweight:", self.bodyweight_spin)

        self.notes_edit = QLineEdit()
        form.addRow("Notes:", self.notes_edit)

        layout.addLayout(form)

        if entry is not None:
            self.date_edit.setDate(QDate(entry.recorded_at.year, entry.recorded_at.month, entry.recorded_at.day))
            self.bodyweight_spin.setValue(entry.bodyweight or 0.0)
            self.notes_edit.setText(entry.notes or "")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _validate_and_accept(self):
        if self.bodyweight_spin.value() <= 0:
            QMessageBox.warning(self, "Warning", "Bodyweight must be greater than zero.")
            return
        self.accept()

    def get_data(self):
        qdate = self.date_edit.date()
        return {
            "recorded_at": qdate.toPython(),
            "bodyweight": self.bodyweight_spin.value(),
            "notes": self.notes_edit.text().strip() or None,
        }
