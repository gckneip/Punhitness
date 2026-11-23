BG_APP = "#f4f6fb"
SURFACE = "#ffffff"
BORDER = "#e1e4eb"
TEXT_PRIMARY = "#1f2430"
TEXT_SECONDARY = "#6b7280"
PRIMARY = "#3462eb"
PRIMARY_HOVER = "#2c53c9"
PRIMARY_PRESSED = "#2445a8"
SELECTION = "#dbe4ff"

BASE_FONT_SIZE = 13
SMALL_FONT_SIZE = round(BASE_FONT_SIZE * 11 / 13)
STAT_VALUE_FONT_SIZE = round(BASE_FONT_SIZE * 20 / 13)


def build_stylesheet() -> str:
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
    background: {BORDER};
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
    background: {BORDER};
    border-color: {PRIMARY};
}}

QPushButton:pressed {{
    background: {SELECTION};
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
}}

QHeaderView::section {{
    background: {BORDER};
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
