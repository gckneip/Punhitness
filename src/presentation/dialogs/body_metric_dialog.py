from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QDateEdit,
    QDialogButtonBox, QVBoxLayout, QMessageBox,
)
from PySide6.QtCore import QDate

from src.presentation.i18n import t


class BodyMetricDialog(QDialog):
    def __init__(self, parent=None, entry=None):
        super().__init__(parent)
        self.setWindowTitle(t("dialog.body_metric.edit_title") if entry else t("dialog.body_metric.new_title"))
        self.setModal(True)
        self.resize(320, 200)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        form.addRow(t("field.date"), self.date_edit)

        self.bodyweight_spin = QDoubleSpinBox()
        self.bodyweight_spin.setRange(0, 500)
        self.bodyweight_spin.setDecimals(1)
        self.bodyweight_spin.setSuffix(" kg")
        form.addRow(t("field.bodyweight"), self.bodyweight_spin)

        self.notes_edit = QLineEdit()
        form.addRow(t("field.notes"), self.notes_edit)

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
            QMessageBox.warning(self, t("common.warning"), t("msg.bodyweight_positive"))
            return
        self.accept()

    def get_data(self):
        qdate = self.date_edit.date()
        return {
            "recorded_at": qdate.toPython(),
            "bodyweight": self.bodyweight_spin.value(),
            "notes": self.notes_edit.text().strip() or None,
        }
