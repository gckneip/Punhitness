from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel


def make_stat_card(title: str, value_label: QLabel) -> QFrame:
    card = QFrame()
    card.setObjectName("statCard")
    card.setMaximumHeight(96)

    layout = QVBoxLayout(card)
    layout.setContentsMargins(14, 10, 14, 10)
    layout.setSpacing(4)
    layout.addStretch()

    title_label = QLabel(title)
    title_label.setObjectName("statCardTitle")
    layout.addWidget(title_label)

    value_label.setObjectName("statCardValue")
    layout.addWidget(value_label)

    layout.addStretch()
    return card
