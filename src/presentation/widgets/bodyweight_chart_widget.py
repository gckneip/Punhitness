import pyqtgraph as pg
from PySide6.QtWidgets import QWidget, QVBoxLayout
from src.presentation import theme
from src.presentation.i18n import t


class BodyweightChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel("left", t("chart.bodyweight"))
        self.plot_widget.setLabel("bottom", t("chart.date"))
        self.plot_widget.showGrid(x=True, y=True, alpha=0.2)
        layout.addWidget(self.plot_widget)

    def set_entries(self, entries):
        """`entries` most-recent-first (as returned by BodyMetricUseCases.list_metrics)."""
        self.plot_widget.clear()
        chronological = list(reversed(entries))
        points = [e for e in chronological if e.bodyweight is not None]
        if not points:
            return
        x = list(range(len(points)))
        y = [p.bodyweight for p in points]
        self.plot_widget.plot(x, y, pen=pg.mkPen(theme.PRIMARY, width=2), symbol="o")
        labels = [p.recorded_at.isoformat() for p in points]
        ticks = [[(i, label) for i, label in enumerate(labels)]]
        self.plot_widget.getAxis("bottom").setTicks(ticks)
