from src.domain.entities.theme import LIGHT_PALETTE

BG_APP = LIGHT_PALETTE.bg_app
SURFACE = LIGHT_PALETTE.surface
BORDER = LIGHT_PALETTE.border
TEXT_PRIMARY = LIGHT_PALETTE.text_primary
TEXT_SECONDARY = LIGHT_PALETTE.text_secondary
PRIMARY = LIGHT_PALETTE.primary
PRIMARY_HOVER = LIGHT_PALETTE.primary_hover
PRIMARY_PRESSED = LIGHT_PALETTE.primary_pressed
SELECTION = LIGHT_PALETTE.selection

# The original design was tuned at a 13px base (small text at 11px, the big
# stat-card value at 20px) - these ratios are pinned to that reference point
# forever, independent of whatever the *default* base size is, so relative
# proportions stay correct at any size the user picks.
_REFERENCE_BASE_FONT_SIZE = 13
_SMALL_FONT_RATIO = 11 / _REFERENCE_BASE_FONT_SIZE
_STAT_VALUE_FONT_RATIO = 20 / _REFERENCE_BASE_FONT_SIZE

DEFAULT_BASE_FONT_SIZE = 13

BASE_FONT_SIZE = DEFAULT_BASE_FONT_SIZE
SMALL_FONT_SIZE = round(DEFAULT_BASE_FONT_SIZE * _SMALL_FONT_RATIO)
STAT_VALUE_FONT_SIZE = round(DEFAULT_BASE_FONT_SIZE * _STAT_VALUE_FONT_RATIO)


def load_font_size(base_size: int) -> None:
    """Mutate this module's font-size globals from a single base size (the
    normal-text size). The other sizes used in the app (small/secondary text,
    the big stat-card value) scale proportionally to it, so the user only
    ever picks one number. Restart-only timing rule as load_palette() below -
    call before any widget is constructed."""
    global BASE_FONT_SIZE, SMALL_FONT_SIZE, STAT_VALUE_FONT_SIZE
    BASE_FONT_SIZE = base_size
    SMALL_FONT_SIZE = round(base_size * _SMALL_FONT_RATIO)
    STAT_VALUE_FONT_SIZE = round(base_size * _STAT_VALUE_FONT_RATIO)


def load_palette(palette) -> None:
    """Mutate this module's color globals from a ThemePalette.

    Restart-only theming: call this exactly once, in main(), after
    AppSettingsUseCases/ThemeUseCases exist but before app.setStyleSheet(),
    configure_pyqtgraph_theme(), or any widget/icon is constructed. Every
    theme.* read-site in src/presentation/ does `from src.presentation import
    theme` (module import) and reads theme.X inside a function/method body,
    so it naturally picks up these new values with zero per-file changes.
    """
    global BG_APP, SURFACE, BORDER, TEXT_PRIMARY, TEXT_SECONDARY
    global PRIMARY, PRIMARY_HOVER, PRIMARY_PRESSED, SELECTION
    BG_APP = palette.bg_app
    SURFACE = palette.surface
    BORDER = palette.border
    TEXT_PRIMARY = palette.text_primary
    TEXT_SECONDARY = palette.text_secondary
    PRIMARY = palette.primary
    PRIMARY_HOVER = palette.primary_hover
    PRIMARY_PRESSED = palette.primary_pressed
    SELECTION = palette.selection


def _hex_to_rgb(value: str):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _mix(hex_a: str, hex_b: str, amount: float) -> str:
    """Blend hex_a toward hex_b by `amount` (0..1), so hover/pressed/disabled/
    alternate-row shades are derived from the active palette instead of a
    hardcoded gray that would look wrong if the palette ever changes."""
    a, b = _hex_to_rgb(hex_a), _hex_to_rgb(hex_b)
    mixed = tuple(round(ca + (cb - ca) * amount) for ca, cb in zip(a, b))
    return "#%02x%02x%02x" % mixed


def configure_pyqtgraph_theme() -> None:
    import pyqtgraph as pg
    pg.setConfigOption("background", SURFACE)
    pg.setConfigOption("foreground", TEXT_SECONDARY)
    pg.setConfigOption("antialias", True)


def build_stylesheet() -> str:
    hover_bg = _mix(SURFACE, BORDER, 0.5)
    pressed_bg = _mix(SURFACE, BORDER, 0.8)
    disabled_bg = _mix(SURFACE, BORDER, 0.35)
    alt_row_bg = _mix(SURFACE, BORDER, 0.15)
    header_bg = _mix(SURFACE, BORDER, 0.3)

    return f"""
* {{
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    font-size: {BASE_FONT_SIZE}px;
    color: {TEXT_PRIMARY};
}}

QMainWindow, QWidget {{
    background: {BG_APP};
}}

QDialog {{
    background: {SURFACE};
}}

QLabel {{
    background: transparent;
}}

QToolTip {{
    background: {TEXT_PRIMARY};
    color: {SURFACE};
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
}}

QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    background: {SURFACE};
    top: -1px;
}}

QTabBar::tab {{
    background: {SURFACE};
    color: {TEXT_SECONDARY};
    padding: 8px 16px;
    margin-right: 2px;
    border: 1px solid {BORDER};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:selected {{
    background: transparent;
    color: {TEXT_PRIMARY};
    font-weight: 600;
    border-color: {BORDER};
}}

QTabBar::tab:hover:!selected {{
    background: {hover_bg};
    border-color: {BORDER};
    color: {TEXT_PRIMARY};
}}

QPushButton {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 14px;
    color: {TEXT_PRIMARY};
}}

QPushButton:hover {{
    background: {hover_bg};
    border-color: {PRIMARY};
}}

QPushButton:pressed {{
    background: {pressed_bg};
}}

QPushButton:disabled {{
    color: {TEXT_SECONDARY};
    background: {disabled_bg};
}}

QPushButton#primaryButton {{
    background: {PRIMARY};
    border: 1px solid {PRIMARY};
    color: white;
    font-weight: 600;
}}

QPushButton#primaryButton:hover {{
    background: {PRIMARY_HOVER};
    border-color: {PRIMARY_HOVER};
}}

QPushButton#primaryButton:pressed {{
    background: {PRIMARY_PRESSED};
}}

QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox, QSpinBox, QTextEdit {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 5px 8px;
    selection-background-color: {SELECTION};
}}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus, QSpinBox:focus, QTextEdit:focus {{
    border: 1px solid {PRIMARY};
}}

QComboBox::drop-down {{
    border: none;
    width: 20px;
}}

QTableWidget {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: {BORDER};
    selection-background-color: {SELECTION};
    selection-color: {TEXT_PRIMARY};
    alternate-background-color: {alt_row_bg};
}}

QHeaderView::section {{
    background: {header_bg};
    color: {TEXT_SECONDARY};
    padding: 6px;
    border: none;
    border-bottom: 1px solid {BORDER};
    font-weight: 600;
}}

QTableWidget::item {{
    padding: 4px;
}}

QFrame#statCard {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}

QLabel#statCardTitle {{
    color: {TEXT_SECONDARY};
    font-size: {SMALL_FONT_SIZE}px;
    font-weight: 600;
}}

QLabel#statCardValue {{
    font-size: {STAT_VALUE_FONT_SIZE}px;
    font-weight: 700;
}}
"""
