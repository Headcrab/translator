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
    QMessageBox,
    QProgressBar,
    QDialog,
)
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from settings_manager import SettingsManager
from .styles import get_style
from .settings_window import SettingsWindow
from llm_api import LLMApi
import os
from qasync import asyncSlot


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    # Сигналы
    clipboard_updated = pyqtSignal(str)
    show_window_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()

        self.setWindowTitle("Мое Python-приложение (PyQt)")
        self.apply_theme()

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

        # Кнопка для перевода текста
        translate_button = QToolButton(self)
        translate_button.setIcon(
            self.style().standardIcon(self.style().SP_BrowserReload)
        )
        translate_button.setIconSize(QSize(20, 20))
        translate_button.setFixedSize(32, 32)
        self.apply_theme()
        translate_button.setToolTip("Перевести")
        self.translate_button = translate_button

        # Дропбокс выбора языка
        language_label = QLabel("Язык:", self)
        self.apply_theme()
        self.language_combo = QComboBox(self)
        self.language_combo.setMinimumWidth(120)
        available_languages, current_language = self.settings_manager.get_languages()
        self.language_combo.addItems(available_languages)
        self.language_combo.setCurrentText(current_language)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)

        # Дропбокс выбора модели
        model_label = QLabel("Модель:", self)
        self.apply_theme()
        self.model_combo = QComboBox(self)
        self.model_combo.setMinimumWidth(150)
        self.update_model_combo()
        self.model_combo.currentTextChanged.connect(self.on_model_changed)

        # Восстанавливаем блок создания кнопки настроек
        # Кнопка для открытия окна настроек
        settings_button = QToolButton(self)
        settings_button.setIcon(
            self.style().standardIcon(self.style().SP_DialogOpenButton)
        )
        settings_button.setIconSize(QSize(20, 20))
        settings_button.setFixedSize(32, 32)
        self.apply_theme()
        settings_button.setToolTip("Настройки")
        settings_button.clicked.connect(self.open_settings)

        # Изменяем порядок добавления виджетов в верхний layout
        top_layout.addWidget(translate_button)
        top_layout.addWidget(language_label)
        top_layout.addWidget(self.language_combo)
        top_layout.addWidget(model_label)
        top_layout.addWidget(self.model_combo)
        top_layout.addStretch()  # Растяжка перед кнопкой настроек
        top_layout.addWidget(settings_button)


        # Создаем центральный виджет и его layout
        central_widget = QWidget(self)
        self.apply_theme()
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
        self.apply_theme()
        source_layout = QVBoxLayout(source_group)
        source_layout.setContentsMargins(8, 8, 8, 8)

        self.text_edit = QTextEdit(self)
        self.apply_theme()
        source_layout.addWidget(self.text_edit)
        texts_layout.addWidget(source_group)

        # Группа для переведенного текста
        translated_group = QGroupBox("Переведенный текст")
        self.apply_theme()
        translated_layout = QVBoxLayout(translated_group)
        translated_layout.setContentsMargins(8, 8, 8, 8)

        self.translated_text = QTextEdit(self)
        self.apply_theme()
        self.translated_text.setReadOnly(True)  # Делаем поле только для чтения
        translated_layout.addWidget(self.translated_text)
        texts_layout.addWidget(translated_group)

        central_layout.addLayout(texts_layout)
        self.setCentralWidget(central_widget)

        # Добавляем прогресс-бар
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Бесконечная анимация
        self.progress_bar.setTextVisible(False)  # Скрыть процентный текст
        self.progress_bar.hide()
        central_layout.addWidget(self.progress_bar)

        self.translate_button.clicked.connect(self.handle_translate_click)

    def update_model_combo(self):
        """Обновляет список моделей в комбобоксе."""
        self.model_combo.clear()
        available_models, current_model = self.settings_manager.get_models()
        model_names = [model["name"] for model in available_models]
        self.model_combo.addItems(model_names)
        if current_model:
            self.model_combo.setCurrentText(current_model)

    async def _do_translate(self):
        """Выполняет перевод текста."""
        source_text = self.text_edit.toPlainText()
        if not source_text:
            return
            
        # Получаем информацию о текущей модели
        model_info = self.settings_manager.get_model_info()
        if not model_info:
            QMessageBox.warning(self, "Ошибка", "Не выбрана модель для перевода")
            return
            
        # Проверяем наличие токена доступа
        if not model_info.get("access_token"):
            QMessageBox.warning(
                self, 
                "Ошибка", 
                "Не указан токен доступа для модели. Пожалуйста, добавьте токен в настройках."
            )
            return
            
        try:
            # Создаем экземпляр API клиента
            api = LLMApi(model_info, self.settings_manager)
            
            # Получаем целевой язык
            target_lang = self.language_combo.currentText()
            
            # Выполняем перевод
            translated = await api.translate(source_text, target_lang)
            
            # Обновляем поле с переведенным текстом
            self.update_translated_text(translated)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    @asyncSlot()
    async def handle_translate_click(self):
        text = self.text_edit.toPlainText()
        if not text:
            return
        
        self.progress_bar.show()
        
        try:
            model_info = self.settings_manager.get_model_info()
            if not model_info:
                self.show_error_message("Модель перевода не выбрана")
                return
            
            llm_api = LLMApi(model_info, self.settings_manager)
            target_lang = self.language_combo.currentText()
            if not model_info.get("access_token"):
                self.show_error_message("Токен доступа не настроен")
                return
            
            translated = await llm_api.translate(text, target_lang)
            if not translated:
                raise ValueError("Пустой ответ от модели")
            
            self.translated_text.setPlainText(translated)
        except Exception as e:
            self.show_error_message(f"Ошибка перевода: {str(e)}")
        finally:
            self.progress_bar.hide()

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
        if self.settings_window.exec_() == QDialog.Accepted:
            self.settings_window.load_settings()

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

    def apply_theme(self):
        """Применяет текущую тему к окну и всем его элементам."""
        theme_mode = self.settings_manager.get_theme()
        style = get_style(theme_mode)
        
        # Применяем стили ко всему окну и его элементам
        self.setStyleSheet(style)
        
        # Обновляем все элементы, которые могут требовать перерисовки
        self.update()

    def show_error_message(self, message):
        QMessageBox.warning(self, "Ошибка", message)

    async def translate_text(self, text: str, target_lang: str) -> str:
        model_info = {
            "provider": "OpenAI",
            "api_endpoint": "https://api.openai.com/v1",
            "model_name": "gpt-3.5-turbo",
            "access_token": os.getenv("OPENAI_API_KEY")
        }
        
        llm = LLMApi(model_info, self.settings_manager)
        return await llm.translate(text, target_lang)
