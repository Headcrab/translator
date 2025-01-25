"""Модуль содержит стили для UI компонентов."""

COMMON_STYLE = """
QDialog {
    background-color: #f5f5f5;
}

QGroupBox {
    border: 2px solid #ddd;
    border-radius: 8px;
    margin-top: 1em;
    padding-top: 10px;
    background-color: white;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #444;
}

QPushButton {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #0056b3;
}

QPushButton:pressed {
    background-color: #004085;
}

QPushButton[text="Отмена"], QPushButton[text="Удалить"] {
    background-color: #6c757d;
}

QPushButton[text="Отмена"]:hover, QPushButton[text="Удалить"]:hover {
    background-color: #5a6268;
}

QComboBox {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px;
    background-color: white;
}

QComboBox:hover {
    border-color: #007bff;
}

QTextEdit, QLineEdit {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px;
    background-color: white;
}

QTextEdit:focus, QLineEdit:focus {
    border-color: #007bff;
}

QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    border: 2px solid #ddd;
    border-radius: 4px;
    background-color: white;
}

QCheckBox::indicator:checked {
    border: 2px solid #007bff;
    border-radius: 4px;
    background-color: #007bff;
}
"""

TOOL_BUTTON_STYLE = """
QToolButton {
    border: 2px solid #ddd;
    border-radius: 20px;
    background-color: white;
    padding: 5px;
}
QToolButton:hover {
    background-color: #f0f0f0;
    border-color: #007bff;
}
QToolButton:pressed {
    background-color: #e0e0e0;
}
"""

TEXT_EDIT_STYLE = """
QTextEdit {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 8px;
    background-color: white;
    selection-background-color: #007bff;
    selection-color: white;
}
QTextEdit:focus {
    border-color: #007bff;
}
"""

GROUP_BOX_STYLE = """
QGroupBox {
    border: 1px solid #ddd;
    border-radius: 4px;
    margin-top: 0.5em;
    background-color: white;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 3px;
    color: #444;
}
"""

LABEL_STYLE = "color: #444; font-weight: bold;"
