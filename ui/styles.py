"""Модуль содержит стили для UI компонентов."""

LIGHT_STYLE = """
QDialog, QMainWindow {
    background-color: #f5f5f5;
    color: #444;
    border: 1px solid #ddd;
}

QMenuBar {
    background-color: #f5f5f5;
    color: #444;
}

QMenuBar::item {
    background-color: #f5f5f5;
    color: #444;
}

QMenuBar::item:selected {
    background-color: #e5e5e5;
}

QMenu {
    background-color: #f5f5f5;
    color: #444;
    border: 1px solid #ddd;
}

QMenu::item:selected {
    background-color: #e5e5e5;
}

QStatusBar {
    background-color: #f5f5f5;
    color: #444;
}

QTitleBar {
    background-color: #f5f5f5;
    color: #444;
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
    color: #444;
}

QComboBox:hover {
    border-color: #007bff;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    color: #444;
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: white;
    color: #444;
    border: 1px solid #ddd;
    selection-background-color: #007bff;
    selection-color: white;
}

QTextEdit, QLineEdit {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px;
    background-color: white;
    color: #444;
}

QTextEdit:focus, QLineEdit:focus {
    border-color: #007bff;
}

QCheckBox {
    spacing: 8px;
    color: #444;
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

QLabel {
    color: #444;
}

QListWidget {
    background-color: white;
    color: #444;
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 5px;
}

QListWidget::item:hover {
    background-color: #f5f5f5;
}

QListWidget::item:selected {
    background-color: #007bff;
    color: white;
}
"""

DARK_STYLE = """
QDialog, QMainWindow {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #333;
}

QMenuBar {
    background-color: #1e1e1e;
    color: #ffffff;
}

QMenuBar::item {
    background-color: #1e1e1e;
    color: #ffffff;
}

QMenuBar::item:selected {
    background-color: #2d2d2d;
}

QMenu {
    background-color: #1e1e1e;
    color: #ffffff;
    border: 1px solid #333;
}

QMenu::item:selected {
    background-color: #2d2d2d;
}

QStatusBar {
    background-color: #1e1e1e;
    color: #ffffff;
}

QTitleBar {
    background-color: #1e1e1e;
    color: #ffffff;
}

QGroupBox {
    border: 1px solid #444;
    border-radius: 8px;
    margin-top: 1em;
    padding-top: 10px;
    background-color: #2d2d2d;
    color: #ffffff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #ffffff;
    background-color: #2d2d2d;
}

QPushButton {
    background-color: #0d6efd;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    min-width: 100px;
}

QPushButton:hover {
    background-color: #0b5ed7;
}

QPushButton:pressed {
    background-color: #0a58ca;
}

QPushButton[text="Отмена"], QPushButton[text="Удалить"] {
    background-color: #6c757d;
}

QPushButton[text="Отмена"]:hover, QPushButton[text="Удалить"]:hover {
    background-color: #5a6268;
}

QComboBox {
    border: 1px solid #444;
    border-radius: 4px;
    padding: 5px;
    background-color: #2d2d2d;
    color: #ffffff;
}

QComboBox:hover {
    border-color: #0d6efd;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    color: #ffffff;
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #444;
    selection-background-color: #0d6efd;
    selection-color: #ffffff;
}

QTextEdit, QLineEdit {
    border: 1px solid #444;
    border-radius: 4px;
    padding: 5px;
    background-color: #2d2d2d;
    color: #ffffff;
}

QTextEdit:focus, QLineEdit:focus {
    border-color: #0d6efd;
}

QCheckBox {
    spacing: 8px;
    color: #ffffff;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
}

QCheckBox::indicator:unchecked {
    border: 2px solid #444;
    border-radius: 4px;
    background-color: #2d2d2d;
}

QCheckBox::indicator:checked {
    border: 2px solid #0d6efd;
    border-radius: 4px;
    background-color: #0d6efd;
}

QLabel {
    color: #ffffff;
}

QVBoxLayout, QHBoxLayout, QVBoxLayout, QGridLayout {
    border: 1px solid #444;
    border-radius: 8px;
    margin-top: 1em;
    padding-top: 10px;
    background-color: #2d2d2d;
    color: #ffffff;
}

QScrollArea {
    background-color: #2d2d2d;
    border: 1px solid #444;
    border-radius: 8px;
    margin-top: 1em;
    padding-top: 10px;
    color: #ffffff;
}

QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background-color: #444;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #555;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background-color: #2d2d2d;
}

QListWidget {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 5px;
}

QListWidget::item:hover {
    background-color: #3d3d3d;
}

QListWidget::item:selected {
    background-color: #0d6efd;
    color: #ffffff;
}
"""

TOOL_BUTTON_LIGHT_STYLE = """
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

TOOL_BUTTON_DARK_STYLE = """
QToolButton {
    border: 2px solid #444;
    border-radius: 20px;
    background-color: #2d2d2d;
    padding: 5px;
}
QToolButton:hover {
    background-color: #3d3d3d;
    border-color: #0d6efd;
}
QToolButton:pressed {
    background-color: #4d4d4d;
}

QProgressBar {
    border: 1px solid #3A3939;
    border-radius: 5px;
    background-color: #201F1F;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #3DAEE9;
    width: 10px;
    margin: 0.5px;
}

"""

def get_style(theme_mode="system"):
    """Возвращает стиль в зависимости от выбранной темы.
    
    Args:
        theme_mode: Режим темы ('light', 'dark' или 'system')
        
    Returns:
        str: Строка со стилями для выбранной темы
    """
    import darkdetect
    
    # Определяем реальный режим темы
    if theme_mode == "system":
        is_dark = darkdetect.isDark()
    else:
        is_dark = theme_mode == "dark"
    
    # Выбираем соответствующие стили
    main_style = DARK_STYLE if is_dark else LIGHT_STYLE
    tool_button_style = TOOL_BUTTON_DARK_STYLE if is_dark else TOOL_BUTTON_LIGHT_STYLE
    
    return main_style + "\n" + tool_button_style

def get_tab_style(theme_mode: str) -> str:
    """Возвращает стили для вкладок в зависимости от темы"""
    if theme_mode == "dark":
        return """
            QTabWidget::pane {
                border: 1px solid #444;
                background: #2d2d2d;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #383838;
                color: #fff;
                padding: 8px 12px;
                margin-right: 2px;
                border: 1px solid #444;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #2d2d2d;
                border-bottom: none;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """
    elif theme_mode == "light":
        return """
            QTabWidget::pane {
                border: 1px solid #ccc;
                background: #fff;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                color: #333;
                padding: 8px 12px;
                margin-right: 2px;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #fff;
                border-bottom: none;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """
    else:  # system
        return """
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                padding: 8px 12px;
                margin-right: 2px;
            }
        """
