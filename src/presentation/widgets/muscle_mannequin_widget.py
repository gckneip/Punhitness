import re
from pathlib import Path
from typing import Dict, List, Optional

from PySide6.QtCore import QByteArray, QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)

from src.domain.entities.exercise import MuscleGroup
from src.presentation import theme
from src.presentation.i18n import t
from src.presentation.icons import icon
from src.presentation.labels import muscle_group_label

# Vendored from Open-Muscle-Map (MIT) — see assets/muscle_map/THIRD_PARTY_NOTICES.md.
_SVG_PATH = Path(__file__).resolve().parent.parent / "assets" / "muscle_map" / "male-muscle-map.svg"

_VIEW_ELEMENT_ID = {"front": "male-front", "rear": "male-rear"}

# The SVG tags each muscle panel with data-muscle-group (e.g. "upper_arms",
# "quadriceps"); this app only filters/tracks by broad group, so several
# collapse onto the same MuscleGroup. None means "rendered, not selectable"
# (neck, joints, tendons/fascia — not a muscle an exercise targets).
_SVG_GROUP_TO_MUSCLE_GROUP: Dict[str, Optional[MuscleGroup]] = {
    "chest": MuscleGroup.CHEST,
    "upper_back": MuscleGroup.BACK,
    "lower_back": MuscleGroup.BACK,
    "shoulders": MuscleGroup.SHOULDERS,
    "upper_arms": MuscleGroup.ARMS,
    "forearms": MuscleGroup.ARMS,
    "core": MuscleGroup.CORE,
    "hips": MuscleGroup.LEGS,
    "adductors": MuscleGroup.LEGS,
    "quadriceps": MuscleGroup.LEGS,
    "shins": MuscleGroup.LEGS,
    "calves": MuscleGroup.LEGS,
    "glutes": MuscleGroup.LEGS,
    "hamstrings": MuscleGroup.LEGS,
    "neck": None,
    "joints": None,
    "connective_tissue": None,
}

# Matches each <g id="male-front-right-pectoralis_major-01" ...> panel wrapper.
_TAG_RE = re.compile(r'<g id="male-(?:front|rear)-(?:left|right)-[a-z_]+-\d+"[^>]*>')
_ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')

# The body outline (head, neck, hands, feet) isn't a muscle panel — it's one
# "silhouette" path per view, baked into the artwork with a fixed dark fill
# (#2a2c37) tuned for a light page. That's nearly invisible against a dark
# theme's background (e.g. Dracula's #282A36), so it's always recolored to
# theme.TEXT_PRIMARY rather than left at its baked-in color.
_SILHOUETTE_RE = re.compile(r'<g id="(male-(?:front|rear)-silhouette-\d+)"')

_HEAT_COLD = QColor("#dfe3ec")
_HEAT_MID = QColor("#f6b93b")
_HEAT_HOT = QColor("#e74c3c")

HEAT_GRADIENT_CSS = (
    "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
    f"stop:0 {_HEAT_COLD.name()}, stop:0.5 {_HEAT_MID.name()}, stop:1 {_HEAT_HOT.name()})"
)

# Flat, maximally-distinct colors used only for the offscreen hit-test mask —
# never shown to the user.
_MASK_COLORS: Dict[MuscleGroup, QColor] = {
    MuscleGroup.CHEST: QColor(237, 28, 36),
    MuscleGroup.BACK: QColor(0, 120, 220),
    MuscleGroup.SHOULDERS: QColor(240, 200, 0),
    MuscleGroup.ARMS: QColor(0, 170, 90),
    MuscleGroup.CORE: QColor(160, 30, 190),
    MuscleGroup.LEGS: QColor(240, 130, 20),
}
_MASK_LOOKUP = {color.rgb(): group for group, color in _MASK_COLORS.items()}


def _mix(c1: QColor, c2: QColor, t: float) -> QColor:
    return QColor(
        round(c1.red() + (c2.red() - c1.red()) * t),
        round(c1.green() + (c2.green() - c1.green()) * t),
        round(c1.blue() + (c2.blue() - c1.blue()) * t),
    )


def _heat_color(t: float) -> str:
    t = max(0.0, min(1.0, t))
    if t <= 0.5:
        return _mix(_HEAT_COLD, _HEAT_MID, t / 0.5).name()
    return _mix(_HEAT_MID, _HEAT_HOT, (t - 0.5) / 0.5).name()


class _MuscleMapAsset:
    """Parsed once per process: the vendored SVG plus a view -> MuscleGroup ->
    element-id index (read from each panel's data-view/data-muscle-group
    attributes), used to build CSS-recolored display SVGs and a flat
    id-color hit-test mask on demand."""

    def __init__(self, svg_path: Path = _SVG_PATH):
        self.raw = svg_path.read_bytes()
        text = self.raw.decode("utf-8")

        self.silhouette_ids: List[str] = _SILHOUETTE_RE.findall(text)

        self.ids_by_view_group: Dict[str, Dict[MuscleGroup, List[str]]] = {"front": {}, "rear": {}}
        for tag in _TAG_RE.findall(text):
            attrs = dict(_ATTR_RE.findall(tag))
            view = attrs.get("data-view")
            element_id = attrs.get("id")
            if view not in ("front", "rear") or not element_id:
                continue
            group = _SVG_GROUP_TO_MUSCLE_GROUP.get(attrs.get("data-muscle-group", ""))
            if group is None:
                continue
            self.ids_by_view_group[view].setdefault(group, []).append(element_id)

        self.ids_by_group_any_view: Dict[MuscleGroup, List[str]] = {}
        for view_ids in self.ids_by_view_group.values():
            for group, ids in view_ids.items():
                self.ids_by_group_any_view.setdefault(group, []).extend(ids)

        self._mask_bytes_cache: Dict[str, bytes] = {}

    def _svg_tag_end(self) -> int:
        return self.raw.index(b">", self.raw.index(b"<svg")) + 1

    def display_bytes(self, color_overrides: Dict[MuscleGroup, str], skin_color: str) -> bytes:
        """Base artwork with specific muscle-group panels (across both views)
        recolored via an injected <style> block. Targeting the panel's nested
        path (not the <g> wrapper) is required — the path's own fill
        attribute otherwise wins over a rule on its ancestor. The silhouette
        (head/neck/hands/feet) is always repainted in skin_color, since its
        baked-in fill has no theme awareness of its own."""
        rules = [f'#{element_id} path{{fill:{skin_color} !important;}}' for element_id in self.silhouette_ids]
        rules += [
            f'#{element_id} path{{fill:{color} !important;}}'
            for group, color in color_overrides.items()
            for element_id in self.ids_by_group_any_view.get(group, [])
        ]
        style = f"<style>{''.join(rules)}</style>".encode("utf-8")
        idx = self._svg_tag_end()
        return self.raw[:idx] + style + self.raw[idx:]

    def mask_bytes(self, view: str) -> bytes:
        """Same artwork, but every panel is flattened to solid white except
        selectable muscle panels, each painted in a unique flat color — a
        pixel-accurate id map for hit testing."""
        cached = self._mask_bytes_cache.get(view)
        if cached is not None:
            return cached
        rules = ["path{fill:#ffffff !important;stroke:#ffffff !important;}"]
        for group, element_ids in self.ids_by_view_group[view].items():
            color = _MASK_COLORS[group].name()
            for element_id in element_ids:
                rules.append(f'#{element_id} path{{fill:{color} !important;stroke:{color} !important;}}')
        style = f"<style>{''.join(rules)}</style>".encode("utf-8")
        idx = self._svg_tag_end()
        result = self.raw[:idx] + style + self.raw[idx:]
        self._mask_bytes_cache[view] = result
        return result


_asset: Optional[_MuscleMapAsset] = None


def _get_asset() -> _MuscleMapAsset:
    global _asset
    if _asset is None:
        _asset = _MuscleMapAsset()
    return _asset


class _MannequinCanvas(QWidget):
    muscle_clicked = Signal(object)  # MuscleGroup or None
    hovered_changed = Signal(str)

    def __init__(self, parent=None, selectable=True):
        super().__init__(parent)
        self._selectable = selectable
        self.setMouseTracking(True)
        self.setMinimumSize(140, 300)

        self._asset = _get_asset()
        self.view = "front"
        self._selected: Optional[MuscleGroup] = None
        self._hovered: Optional[MuscleGroup] = None
        self._intensities: Optional[Dict[MuscleGroup, float]] = None
        self._labels: Optional[Dict[MuscleGroup, str]] = None

        self._display_renderer = QSvgRenderer(QByteArray(self._asset.raw))
        self._mask_image: Optional[QImage] = None
        self._mask_view: Optional[str] = None
        self._mask_size: Optional[QSize] = None
        self._fit_target = QRectF()
        self._rebuild_display_renderer()

    def sizeHint(self):
        return QSize(230, 480)

    def set_view(self, view: str):
        if view == self.view:
            return
        self.view = view
        self._hovered = None
        self._mask_image = None
        self.update()

    def set_selected(self, group: Optional[MuscleGroup]):
        self._selected = group
        self._rebuild_display_renderer()

    def set_intensities(self, intensities, labels):
        self._intensities = intensities
        self._labels = labels
        self._rebuild_display_renderer()

    def _rebuild_display_renderer(self):
        overrides: Dict[MuscleGroup, str] = {}
        if self._intensities is not None:
            for group, intensity in self._intensities.items():
                overrides[group] = _heat_color(intensity)
        else:
            if self._selected is not None:
                overrides[self._selected] = theme.PRIMARY
            if self._hovered is not None and self._hovered != self._selected:
                overrides[self._hovered] = theme.SELECTION
        data = self._asset.display_bytes(overrides, theme.TEXT_PRIMARY)
        self._display_renderer = QSvgRenderer(QByteArray(data))
        self.update()

    @staticmethod
    def _fit_rect(bounds: QRectF, size: QSize) -> QRectF:
        if bounds.width() <= 0 or bounds.height() <= 0 or size.width() <= 0 or size.height() <= 0:
            return QRectF(0, 0, size.width(), size.height())
        scale = min(size.width() / bounds.width(), size.height() / bounds.height()) * 0.94
        target_w, target_h = bounds.width() * scale, bounds.height() * scale
        return QRectF((size.width() - target_w) / 2, (size.height() - target_h) / 2, target_w, target_h)

    def _ensure_mask(self):
        size = self.size()
        if (
            self._mask_image is not None
            and self._mask_view == self.view
            and self._mask_size == size
        ):
            return
        if size.width() <= 0 or size.height() <= 0:
            return
        renderer = QSvgRenderer(QByteArray(self._asset.mask_bytes(self.view)))
        element_id = _VIEW_ELEMENT_ID[self.view]
        bounds = renderer.boundsOnElement(element_id)
        self._fit_target = self._fit_rect(bounds, size)

        image = QImage(size, QImage.Format_ARGB32)
        image.fill(QColor("white"))
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing, False)
        renderer.render(painter, element_id, self._fit_target)
        painter.end()

        self._mask_image = image
        self._mask_view = self.view
        self._mask_size = size

    def _region_at(self, pos: QPointF) -> Optional[MuscleGroup]:
        self._ensure_mask()
        if self._mask_image is None:
            return None
        x, y = int(pos.x()), int(pos.y())
        if not (0 <= x < self._mask_image.width() and 0 <= y < self._mask_image.height()):
            return None
        return _MASK_LOOKUP.get(self._mask_image.pixelColor(x, y).rgb())

    def _caption_for(self, group: Optional[MuscleGroup]) -> str:
        if group is None:
            return ""
        label = muscle_group_label(group)
        if self._labels and group in self._labels:
            return f"{label} — {self._labels[group]}"
        return label

    def mouseMoveEvent(self, event):
        group = self._region_at(event.position())
        if group != self._hovered:
            self._hovered = group
            can_interact = group is not None and self._selectable
            self.setCursor(Qt.PointingHandCursor if can_interact else Qt.ArrowCursor)
            self.hovered_changed.emit(self._caption_for(group))
            if self._selectable and self._intensities is None:
                self._rebuild_display_renderer()
            else:
                self.update()

    def leaveEvent(self, event):
        if self._hovered is not None:
            self._hovered = None
            self.hovered_changed.emit("")
            if self._selectable and self._intensities is None:
                self._rebuild_display_renderer()
        self.setCursor(Qt.ArrowCursor)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if not self._selectable:
            return
        group = self._region_at(event.position())
        if group is None:
            return
        self._selected = None if self._selected == group else group
        self._rebuild_display_renderer()
        self.muscle_clicked.emit(self._selected)

    def resizeEvent(self, event):
        self._mask_image = None
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        self._ensure_mask()
        element_id = _VIEW_ELEMENT_ID[self.view]
        target = self._fit_target if self._mask_image is not None else self._fit_rect(
            self._display_renderer.boundsOnElement(element_id), self.size()
        )
        self._display_renderer.render(painter, element_id, target)


class _HeatChip(QWidget):
    """Read-only legend row for a non-body group (Cardio / Full Body): a
    color swatch plus a label, used in heatmap/dashboard mode."""

    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._swatch = QFrame()
        self._swatch.setFixedSize(12, 12)
        self._set_color("#c3c9d6")
        layout.addWidget(self._swatch)
        self._label = QLabel(name)
        self._label.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
        layout.addWidget(self._label)
        layout.addStretch()
        self._name = name

    def _set_color(self, color: str):
        self._swatch.setStyleSheet(f"background: {color}; border-radius: 3px;")

    def set_value(self, intensity: float, extra_text: str = ""):
        self._set_color(_heat_color(intensity))
        self._label.setText(f"{self._name} — {extra_text}" if extra_text else self._name)


class MuscleMannequinWidget(QWidget):
    """A front/rear mannequin built from a real (MIT-licensed) muscle map
    SVG, split into clickable/hoverable muscle-group panels. In selectable
    mode it's a muscle filter (click toggles selection, emits
    muscle_clicked); otherwise it's read-only and driven by
    set_intensities(), used to render "how worked" each muscle is."""

    muscle_clicked = Signal(object)  # MuscleGroup or None

    def __init__(self, parent=None, selectable=True, title: Optional[str] = None, show_legend=False):
        super().__init__(parent)
        self._selectable = selectable
        self._selected: Optional[MuscleGroup] = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(f"font-weight: 600; color: {theme.TEXT_PRIMARY};")
            layout.addWidget(title_label)

        header = QHBoxLayout()
        header.addStretch()
        self._view_btn = QPushButton()
        self._view_btn.setIcon(icon("fa5s.sync-alt"))
        self._view_btn.setToolTip(t("mannequin.switch_to_back"))
        self._view_btn.setFixedSize(28, 28)
        self._view_btn.setCursor(Qt.PointingHandCursor)
        self._view_btn.clicked.connect(self._toggle_view)
        header.addWidget(self._view_btn)
        layout.addLayout(header)

        self._canvas = _MannequinCanvas(selectable=selectable)
        self._canvas.hovered_changed.connect(self._on_hover_changed)
        self._canvas.muscle_clicked.connect(self._on_body_clicked)
        layout.addWidget(self._canvas, 1)

        self._caption = QLabel(" ")
        self._caption.setAlignment(Qt.AlignCenter)
        self._caption.setStyleSheet(f"color: {theme.TEXT_SECONDARY};")
        self._caption.setWordWrap(True)
        layout.addWidget(self._caption)

        if selectable:
            extras_row = QHBoxLayout()
            self._cardio_btn = QPushButton(muscle_group_label(MuscleGroup.CARDIO))
            self._cardio_btn.setCheckable(True)
            self._cardio_btn.setCursor(Qt.PointingHandCursor)
            self._cardio_btn.clicked.connect(lambda: self._on_extra_clicked(MuscleGroup.CARDIO))
            self._full_body_btn = QPushButton(muscle_group_label(MuscleGroup.FULL_BODY))
            self._full_body_btn.setCheckable(True)
            self._full_body_btn.setCursor(Qt.PointingHandCursor)
            self._full_body_btn.clicked.connect(lambda: self._on_extra_clicked(MuscleGroup.FULL_BODY))
            extras_row.addWidget(self._cardio_btn)
            extras_row.addWidget(self._full_body_btn)
            layout.addLayout(extras_row)
        else:
            self._cardio_chip = _HeatChip(muscle_group_label(MuscleGroup.CARDIO))
            self._full_body_chip = _HeatChip(muscle_group_label(MuscleGroup.FULL_BODY))
            layout.addWidget(self._cardio_chip)
            layout.addWidget(self._full_body_chip)

        if show_legend:
            legend_row = QHBoxLayout()
            less_label = QLabel(t("mannequin.legend.less"))
            more_label = QLabel(t("mannequin.legend.more"))
            for label in (less_label, more_label):
                label.setStyleSheet(f"color: {theme.TEXT_SECONDARY}; font-size: {theme.SMALL_FONT_SIZE}px;")
            bar = QFrame()
            bar.setFixedHeight(10)
            bar.setStyleSheet(f"border-radius: 5px; background: {HEAT_GRADIENT_CSS};")
            legend_row.addWidget(less_label)
            legend_row.addWidget(bar, 1)
            legend_row.addWidget(more_label)
            layout.addLayout(legend_row)

    def _toggle_view(self):
        going_to_rear = self._canvas.view == "front"
        self._canvas.set_view("rear" if going_to_rear else "front")
        self._view_btn.setToolTip(t("mannequin.switch_to_front") if going_to_rear else t("mannequin.switch_to_back"))

    def _on_hover_changed(self, text: str):
        self._caption.setText(text or " ")

    def _on_body_clicked(self, group: Optional[MuscleGroup]):
        self._selected = group
        if self._selectable:
            self._cardio_btn.setChecked(False)
            self._full_body_btn.setChecked(False)
        self.muscle_clicked.emit(group)

    def _on_extra_clicked(self, group: MuscleGroup):
        own_btn = self._cardio_btn if group == MuscleGroup.CARDIO else self._full_body_btn
        other_btn = self._full_body_btn if group == MuscleGroup.CARDIO else self._cardio_btn
        other_btn.setChecked(False)
        self._selected = group if own_btn.isChecked() else None
        self._canvas.set_selected(self._selected if self._selected not in (MuscleGroup.CARDIO, MuscleGroup.FULL_BODY) else None)
        self.muscle_clicked.emit(self._selected)

    def set_selected(self, group: Optional[MuscleGroup]):
        self._selected = group
        if self._selectable:
            self._cardio_btn.setChecked(group == MuscleGroup.CARDIO)
            self._full_body_btn.setChecked(group == MuscleGroup.FULL_BODY)
        self._canvas.set_selected(group if group not in (MuscleGroup.CARDIO, MuscleGroup.FULL_BODY) else None)

    def set_intensities(self, intensities: Dict[MuscleGroup, float], labels: Optional[Dict[MuscleGroup, str]] = None):
        body_intensities = {
            g: intensity for g, intensity in intensities.items()
            if g not in (MuscleGroup.CARDIO, MuscleGroup.FULL_BODY)
        }
        self._canvas.set_intensities(body_intensities, labels)
        if not self._selectable:
            labels = labels or {}
            self._cardio_chip.set_value(
                intensities.get(MuscleGroup.CARDIO, 0.0), labels.get(MuscleGroup.CARDIO, "")
            )
            self._full_body_chip.set_value(
                intensities.get(MuscleGroup.FULL_BODY, 0.0), labels.get(MuscleGroup.FULL_BODY, "")
            )

    def clear_intensities(self):
        self._canvas.set_intensities(None, None)
