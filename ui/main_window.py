"""Главное окно приложения."""

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QToolButton,
    QTextEdit,
    QComboBox,
    QLabel,
    QGroupBox,
)
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from settings_manager import SettingsManager
from .styles import (
    COMMON_STYLE,
    TOOL_BUTTON_STYLE,
    TEXT_EDIT_STYLE,
    GROUP_BOX_STYLE,
    LABEL_STYLE,
)
from .settings_window import SettingsWindow


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    # Сигналы
    clipboard_updated = pyqtSignal(str)
    show_window_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()

        self.setWindowTitle("Мое Python-приложение (PyQt)")
        self.setStyleSheet(COMMON_STYLE)

        # Устанавливаем геометрию из настроек
        x, y, width, height = self.settings_manager.get_window_geometry()
        self.setGeometry(x, y, width, height)

        # Подключение сигналов к слотам
        self.clipboard_updated.connect(self.update_clipboard)
        self.show_window_requested.connect(self.show_window)

        self._setup_ui()

        self.settings_window = SettingsWindow(self)

        # Проверяем, нужно ли запускать свернутым
        start_minimized, _ = self.settings_manager.get_behavior()
        if start_minimized:
            self.showMinimized()
        else:
            self.show()

    def _setup_ui(self):
        """Настройка пользовательского интерфейса."""
        # Создаем верхний виджет для кнопок и комбобоксов
        top_widget = QWidget(self)
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(10, 10, 10, 5)
        top_layout.setSpacing(5)

        # Кнопка для открытия окна настроек
        settings_button = QToolButton(self)
        settings_button.setIcon(
            self.style().standardIcon(self.style().SP_DialogOpenButton)
        )
        settings_button.setIconSize(QSize(20, 20))
        settings_button.setFixedSize(32, 32)
        settings_button.setStyleSheet(TOOL_BUTTON_STYLE)
        settings_button.setToolTip("Настройки")
        settings_button.clicked.connect(self.open_settings)

        # Кнопка для перевода текста
        translate_button = QToolButton(self)
        translate_button.setIcon(
            self.style().standardIcon(self.style().SP_BrowserReload)
        )
        translate_button.setIconSize(QSize(20, 20))
        translate_button.setFixedSize(32, 32)
        translate_button.setStyleSheet(TOOL_BUTTON_STYLE)
        translate_button.setToolTip("Перевести")
        translate_button.clicked.connect(self.translate_text)

        # Дропбокс выбора языка
        language_label = QLabel("Язык:", self)
        language_label.setStyleSheet(LABEL_STYLE)
        self.language_combo = QComboBox(self)
        self.language_combo.setMinimumWidth(120)
        available_languages, current_language = self.settings_manager.get_languages()
        self.language_combo.addItems(available_languages)
        self.language_combo.setCurrentText(current_language)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)

        # Дропбокс выбора модели
        model_label = QLabel("Модель:", self)
        model_label.setStyleSheet(LABEL_STYLE)
        self.model_combo = QComboBox(self)
        self.model_combo.setMinimumWidth(150)
        self.update_model_combo()
        self.model_combo.currentTextChanged.connect(self.on_model_changed)

        # Добавляем виджеты в верхний layout
        top_layout.addWidget(settings_button)
        top_layout.addWidget(translate_button)
        top_layout.addWidget(language_label)
        top_layout.addWidget(self.language_combo)
        top_layout.addWidget(model_label)
        top_layout.addWidget(self.model_combo)
        top_layout.addStretch()  # Добавляем растяжку справа

        # Создаем центральный виджет и его layout
        central_widget = QWidget(self)
        central_widget.setStyleSheet("QWidget { background-color: #f5f5f5; }")
        central_layout = QVBoxLayout(central_widget)
        central_layout.setContentsMargins(10, 0, 10, 10)
        central_layout.setSpacing(8)

        # Добавляем верхний виджет в центральный layout
        central_layout.addWidget(top_widget)

        # Создаем горизонтальный layout для текстовых полей
        texts_layout = QHBoxLayout()
        texts_layout.setSpacing(8)

        # Группа для исходного текста
        source_group = QGroupBox("Исходный текст")
        source_group.setStyleSheet(GROUP_BOX_STYLE)
        source_layout = QVBoxLayout(source_group)
        source_layout.setContentsMargins(8, 8, 8, 8)

        self.text_edit = QTextEdit(self)
        self.text_edit.setStyleSheet(TEXT_EDIT_STYLE)
        source_layout.addWidget(self.text_edit)
        texts_layout.addWidget(source_group)

        # Группа для переведенного текста
        translated_group = QGroupBox("Переведенный текст")
        translated_group.setStyleSheet(GROUP_BOX_STYLE)
        translated_layout = QVBoxLayout(translated_group)
        translated_layout.setContentsMargins(8, 8, 8, 8)

        self.translated_text = QTextEdit(self)
        self.translated_text.setStyleSheet(TEXT_EDIT_STYLE)
        self.translated_text.setReadOnly(True)  # Делаем поле только для чтения
        translated_layout.addWidget(self.translated_text)
        texts_layout.addWidget(translated_group)

        central_layout.addLayout(texts_layout)
        self.setCentralWidget(central_widget)

    def update_model_combo(self):
        """Обновляет список моделей в комбобоксе."""
        self.model_combo.clear()
        available_models, current_model = self.settings_manager.get_models()
        model_names = [model["name"] for model in available_models]
        self.model_combo.addItems(model_names)
        if current_model:
            self.model_combo.setCurrentText(current_model)

    def translate_text(self):
        """Обработчик нажатия кнопки перевода."""
        source_text = self.text_edit.toPlainText()
        if not source_text:
            return

        # TODO: Здесь будет логика перевода текста
        # Пока просто заглушка для демонстрации
        translated = f"Перевод: {source_text}"
        self.update_translated_text(translated)

    def update_clipboard(self, text):
        """Слот для обновления буфера обмена"""
        self.text_edit.setText(text)
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        print(f"Слот `update_clipboard` вызван с текстом: {text}")

    def changeEvent(self, event):
        """Обработка изменения состояния окна"""
        if event.type() == event.WindowStateChange:
            # Сохраняем геометрию при сворачивании
            if not self.isMinimized():  # Сохраняем только если окно не свернуто
                geometry = self.geometry()
                self.settings_manager.set_window_geometry(
                    geometry.x(), geometry.y(), geometry.width(), geometry.height()
                )
        super().changeEvent(event)

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        # Сохраняем текущую геометрию окна
        geometry = self.geometry()
        self.settings_manager.set_window_geometry(
            geometry.x(), geometry.y(), geometry.width(), geometry.height()
        )

        # Проверяем настройку сворачивания в трей
        _, minimize_to_tray = self.settings_manager.get_behavior()
        if minimize_to_tray:
            event.ignore()
            self.hide()
        else:
            event.accept()

    def open_settings(self):
        """Открывает окно настроек."""
        self.settings_window.show()

    def on_language_changed(self, language):
        """Обработчик изменения языка в дропбоксе."""
        self.settings_manager.set_current_language(language)

    def on_model_changed(self, model_name):
        """Обработчик изменения модели в дропбоксе."""
        if model_name:
            self.settings_manager.set_current_model(model_name)

    def show_window(self):
        """Показывает и разворачивает окно приложения."""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()

    def update_translated_text(self, text):
        """Обновляет поле с переведенным текстом."""
        self.translated_text.setText(text)
