import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
from src.presentation import theme
from src.presentation.i18n import t
from src.presentation.labels import exercise_name_label


class ProgressChartWidget(QWidget):
    """Lets the user pick an exercise and plots its estimated-1RM trend."""

    def __init__(self, progress_service, parent=None):
        super().__init__(parent)
        self._progress_service = progress_service
        self._exercises = []

        layout = QVBoxLayout(self)
        picker_row = QHBoxLayout()
        picker_row.addWidget(QLabel(t("chart.exercise_label")))
        self.exercise_combo = QComboBox()
        self.exercise_combo.currentIndexChanged.connect(self._refresh_plot)
        picker_row.addWidget(self.exercise_combo)
        picker_row.addStretch()
        layout.addLayout(picker_row)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel("left", t("chart.estimated_1rm"))
        self.plot_widget.setLabel("bottom", t("chart.date"))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        layout.addWidget(self.plot_widget)

    def set_exercise_catalog(self, exercises):
        self._exercises = list(exercises)
        self.exercise_combo.blockSignals(True)
        self.exercise_combo.clear()
        for exercise in self._exercises:
            self.exercise_combo.addItem(exercise_name_label(exercise.name), exercise.id)
        self.exercise_combo.blockSignals(False)
        self._refresh_plot()

    def _refresh_plot(self):
        self.plot_widget.clear()
        exercise_id = self.exercise_combo.currentData()
        if exercise_id is None:
            return
        points = self._progress_service.get_exercise_history(exercise_id)
        if not points:
            return
        x = list(range(len(points)))
        y = [p.estimated_1rm for p in points]
        self.plot_widget.plot(x, y, pen=pg.mkPen(theme.PRIMARY, width=2), symbol="o")
        labels = [p.session_date.isoformat() for p in points]
        ticks = [[(i, label) for i, label in enumerate(labels)]]
        self.plot_widget.getAxis("bottom").setTicks(ticks)
