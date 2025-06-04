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
from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QSize,
)
from settings_manager import SettingsManager
from .styles import get_style
from .settings_window import SettingsWindow
from llm_api import LLMApi
import os
from qasync import asyncSlot
from PyQt5.QtGui import QFont, QTextCursor, QIcon
from ui.events import UpdateTranslationEvent
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
import asyncio
from . import resources_rc  # noqa: F401


class TextEditWithCopyButton(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Создаем кнопку копирования
        self.copy_button = QToolButton(self)
        self.copy_button.setIcon(
            self.style().standardIcon(self.style().SP_DialogSaveButton)
        )
        self.copy_button.setIconSize(QSize(16, 16))
        self.copy_button.setFixedSize(28, 28)
        # Стиль кнопки будет применяться через общую тему

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Позиционируем кнопку в правом верхнем углу с учетом полосы прокрутки
        scrollbar_width = (
            self.verticalScrollBar().width()
            if self.verticalScrollBar().isVisible()
            else 0
        )
        self.copy_button.move(
            self.width() - self.copy_button.width() - scrollbar_width - 8, 5
        )


class MainWindow(QMainWindow):
    """Главное окно приложения."""

    # Сигналы
    clipboard_updated = pyqtSignal(str)
    show_window_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()

        self.setWindowTitle("LLM Translator")
        self.setWindowIcon(QIcon(":/icons/icon.png"))  # Устанавливаем иконку окна

        # Устанавливаем геометрию из настроек
        x, y, width, height = self.settings_manager.get_window_geometry()
        self.setGeometry(x, y, width, height)

        # Подключение сигналов к слотам
        self.clipboard_updated.connect(self.update_clipboard)
        self.show_window_requested.connect(self.show_window)

        self.current_translation_task = None  # Текущая задача перевода
        self._translation_tasks = set()

        self._setup_ui()

        self.settings_window = SettingsWindow(self)

        # Проверяем, нужно ли запускать свернутым
        start_minimized, _ = self.settings_manager.get_behavior()
        if start_minimized:
            self.showMinimized()
        else:
            self.show()

        self.apply_font_settings()

        self.setup_shortcuts()

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
        translate_button.setToolTip("Перевести")
        self.translate_button = translate_button

        # Дропбокс выбора языка
        language_label = QLabel("Язык:", self)
        self.language_combo = QComboBox(self)
        self.language_combo.setMinimumWidth(120)
        available_languages, current_language = self.settings_manager.get_languages()
        for lang in available_languages:
            self.language_combo.addItem(
                self.style().standardIcon(self.style().SP_MessageBoxInformation), lang
            )
        self.language_combo.setCurrentText(current_language)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)

        # Дропбокс выбора модели
        model_label = QLabel("Модель:", self)
        self.model_combo = QComboBox(self)
        self.model_combo.setMinimumWidth(150)
        models, current_model = self.settings_manager.get_models()
        for model in models:
            self.model_combo.addItem(
                self.style().standardIcon(self.style().SP_ComputerIcon), model["name"]
            )
        if current_model:
            self.model_combo.setCurrentText(current_model["name"])
        self.model_combo.currentTextChanged.connect(self.on_model_changed)

        # Дропбокс выбора системного промпта
        prompt_label = QLabel("Промпт:", self)
        self.prompt_combo = QComboBox(self)
        self.prompt_combo.setMinimumWidth(150)
        prompts, current_prompt = self.settings_manager.get_prompts()
        for prompt in prompts:
            self.prompt_combo.addItem(
                self.style().standardIcon(self.style().SP_FileIcon), prompt["name"]
            )
        if current_prompt:
            self.prompt_combo.setCurrentText(current_prompt["name"])
        self.prompt_combo.currentTextChanged.connect(self.on_prompt_changed)

        # Восстанавливаем блок создания кнопки настроек
        # Кнопка для открытия окна настроек
        settings_button = QToolButton(self)
        settings_button.setIcon(
            self.style().standardIcon(self.style().SP_DialogOpenButton)
        )
        settings_button.setIconSize(QSize(20, 20))
        settings_button.setFixedSize(32, 32)
        settings_button.setToolTip("Настройки")
        settings_button.clicked.connect(self.open_settings)

        # Изменяем порядок добавления виджетов в верхний layout
        top_layout.addWidget(translate_button)
        top_layout.addWidget(language_label)
        top_layout.addWidget(self.language_combo)
        top_layout.addWidget(model_label)
        top_layout.addWidget(self.model_combo)
        top_layout.addWidget(prompt_label)
        top_layout.addWidget(self.prompt_combo)
        top_layout.addStretch()  # Растяжка перед кнопкой настроек
        top_layout.addWidget(settings_button)

        # Создаем центральный виджет и его layout
        central_widget = QWidget(self)
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
        source_layout = QVBoxLayout(source_group)
        source_layout.setContentsMargins(8, 8, 8, 8)

        self.text_edit = QTextEdit(self)
        source_layout.addWidget(self.text_edit)
        texts_layout.addWidget(source_group)

        # Группа для переведенного текста
        translated_group = QGroupBox("Переведенный текст")
        translated_layout = QVBoxLayout(translated_group)
        translated_layout.setContentsMargins(8, 8, 8, 8)

        # Создаем текстовое поле с кнопкой копирования
        self.translated_text = TextEditWithCopyButton(self)
        self.translated_text.setReadOnly(True)  # Делаем поле только для чтения
        self.translated_text.copy_button.setToolTip("Копировать перевод")
        self.translated_text.copy_button.clicked.connect(self.copy_translation)

        translated_layout.addWidget(self.translated_text)
        texts_layout.addWidget(translated_group)

        central_layout.addLayout(texts_layout)
        self.setCentralWidget(central_widget)

        # Создаем горизонтальный макет для прогресс-бара и кнопки отмены
        status_layout = QHBoxLayout()

        # Добавляем прогресс-бар
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Бесконечная анимация
        self.progress_bar.setTextVisible(False)  # Скрыть процентный текст
        self.progress_bar.hide()
        status_layout.addWidget(self.progress_bar)

        # Создаем кнопку отмены перевода
        self.cancel_button = QToolButton(self)
        self.cancel_button.setIcon(QIcon(":/icons/cancel.svg"))
        self.cancel_button.setIconSize(QSize(20, 20))
        self.cancel_button.setFixedSize(16, 16)
        self.cancel_button.setToolTip("Отменить перевод")
        self.cancel_button.clicked.connect(self.cancel_translation)
        self.cancel_button.hide()  # Скрыта по умолчанию
        status_layout.addWidget(self.cancel_button)

        # Добавляем горизонтальный макет с прогресс-баром и кнопкой отмены в центральный макет
        central_layout.addLayout(status_layout)

        self.translate_button.clicked.connect(self.start_translation)

    def update_model_combo(self):
        """Обновляет список моделей в выпадающем меню."""
        self.model_combo.clear()
        models, current_model = self.settings_manager.get_models()

        # Добавляем модели в список
        for model in models:
            self.model_combo.addItem(
                self.style().standardIcon(self.style().SP_ComputerIcon), model["name"]
            )

        # Устанавливаем текущую модель
        if current_model:
            index = self.model_combo.findText(current_model["name"])
            if index >= 0:
                self.model_combo.setCurrentIndex(index)

    def update_prompt_combo(self):
        """Обновляет список системных промптов в выпадающем меню."""
        self.prompt_combo.clear()
        prompts, current_prompt = self.settings_manager.get_prompts()
        for prompt in prompts:
            self.prompt_combo.addItem(
                self.style().standardIcon(self.style().SP_FileIcon), prompt["name"]
            )

        if current_prompt:
            self.prompt_combo.setCurrentText(current_prompt["name"])

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
                "Не указан токен доступа для модели. Пожалуйста, добавьте токен в настройках.",
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
    async def start_translation(self):
        """Запускает процесс перевода с учетом режима streaming."""
        try:
            self.cancel_button.show()  # Показываем кнопку отмены
            task = asyncio.create_task(self._start_translation_async())
            self.current_translation_task = task
            self._translation_tasks.add(task)
            task.add_done_callback(lambda t: self._translation_tasks.discard(t))
        except Exception as e:
            self.show_error_message(str(e))

    async def handle_streaming_translation(self):
        """Обрабатывает потоковый перевод."""
        self.progress_bar.show()
        self.translated_text.clear()

        text = self.text_edit.toPlainText()
        target_lang = self.language_combo.currentText()
        model_config = self.get_selected_model_config()

        try:
            llm_api = LLMApi(model_config, self.settings_manager)
            # Создаем асинхронную лямбда-функцию для callback
            await llm_api.translate(
                text, target_lang, streaming_callback=lambda t: self.update_result(t)
            )
        finally:
            self.progress_bar.hide()

    async def handle_regular_translation(self):
        """Обрабатывает обычный перевод."""
        self.progress_bar.show()

        text = self.text_edit.toPlainText()
        target_lang = self.language_combo.currentText()
        model_config = self.get_selected_model_config()

        try:
            llm_api = LLMApi(model_config, self.settings_manager)
            translated = await llm_api.translate(text, target_lang)
            self.translated_text.setText(translated)
        finally:
            self.progress_bar.hide()

    @asyncSlot()
    async def on_clipboard_updated(self, text):
        try:
            self.progress_bar.show()
            translation = await self.llm_api.translate(
                text, self.target_lang, self.handle_streaming_response
            )
            self.update_translation(translation)
        except Exception as e:
            print(f"Translation error: {e}")
            self.translation_area.setPlainText("Ошибка перевода")
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
        """Переопределяем закрытие окна для скрытия в трей и сохранение геометрии"""
        geometry = self.geometry()
        self.settings_manager.set_window_geometry(
            geometry.x(), geometry.y(), geometry.width(), geometry.height()
        )
        self.cancel_translation()
        event.ignore()
        self.hide()

    def open_settings(self):
        """Открывает окно настроек."""
        # Загружаем настройки перед показом окна
        self.settings_window.load_settings()

        if self.settings_window.exec_() == QDialog.Accepted:
            self.apply_font_settings()

            # Получаем выбранную в настройках модель
            selected_item = self.settings_window.models_list.currentItem()
            if selected_item:
                model_name = selected_item.text()
                # Обновляем модель в комбобоксе
                index = self.model_combo.findText(model_name)
                if index >= 0:
                    self.model_combo.setCurrentIndex(index)
                    self.settings_manager.set_current_model(model_name)

    def on_language_changed(self, language):
        """Обработчик изменения языка в дропбоксе."""
        self.settings_manager.set_current_language(language)

    def on_model_changed(self, model_name):
        """Обработчик изменения модели в дропбоксе."""
        if model_name:
            self.settings_manager.set_current_model(model_name)

    def on_prompt_changed(self, prompt_name):
        """Обработчик изменения системного промпта в дропбоксе."""
        if prompt_name:
            self.settings_manager.set_current_prompt(prompt_name)

    def show_window(self):
        """Показывает и активирует окно приложения"""
        self.show()
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.activateWindow()
        self.raise_()  # Поднимаем окно поверх остальных

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
            "access_token": os.getenv("OPENAI_API_KEY"),
        }

        llm = LLMApi(model_info, self.settings_manager)
        return await llm.translate(text, target_lang)

    def apply_font_settings(self):
        """Применяем настройки шрифта к текстовым областям"""
        settings = SettingsManager().get_font_settings()
        font = QFont()
        font.setFamily(settings["font_family"])
        font.setPointSize(int(settings["font_size"]))

        # Применяем шрифт напрямую к существующим виджетам
        self.text_edit.setFont(font)
        self.translated_text.setFont(font)

    def show_settings(self):
        settings_dialog = SettingsWindow(self)
        if settings_dialog.exec_():
            # Применяем новые настройки при подтверждении
            self.apply_font_settings()

    def apply_font(self, font_family, font_size):
        font = QFont(font_family, int(font_size))
        # self.setFont(font)

        self.text_edit.setFont(font)
        self.translated_text.setFont(font)

    async def update_result(self, text):
        """Асинхронное обновление текста перевода с обработкой специальных маркеров"""
        if not text or text.startswith("[DONE]"):
            return
        if text.startswith("[META]"):
            self.statusBar().showMessage(text[6:], 5000)
            return

        # Добавляем текст и автоматически прокручиваем
        self.translated_text.moveCursor(QTextCursor.End)
        self.translated_text.insertPlainText(text)
        self.translated_text.ensureCursorVisible()
        QApplication.processEvents()

    def get_selected_model_config(self):
        """Возвращает конфигурацию выбранной модели."""
        model_name = self.model_combo.currentText()
        return self.settings_manager.get_model_info(model_name)

    def event(self, event):
        if isinstance(event, UpdateTranslationEvent):
            self.translated_text.moveCursor(QTextCursor.End)
            self.translated_text.insertPlainText(event.text)
            self.translated_text.repaint()  # Принудительная перерисовка
            return True
        return super().event(event)

    def setup_shortcuts(self):
        """Настройка горячих клавиш"""
        hide_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        hide_shortcut.activated.connect(self.hide)

        translate_shortcut = QShortcut(
            QKeySequence(Qt.ControlModifier | Qt.Key.Key_Return), self
        )
        translate_shortcut.activated.connect(self.start_translation)

    def wheelEvent(self, event):
        """Обработка вращения колеса мыши с зажатым Ctrl для изменения размера шрифта"""
        if event.modifiers() == Qt.ControlModifier:
            # Получаем текущие настройки шрифта
            settings = self.settings_manager.get_font_settings()
            current_size = settings["font_size"]

            # Определяем направление прокрутки (120 = вверх, -120 = вниз)
            delta = event.angleDelta().y()
            if delta > 0:
                new_size = min(72, current_size + 1)  # Максимальный размер 72
            else:
                new_size = max(8, current_size - 1)  # Минимальный размер 8

            # Сохраняем новые настройки и применяем шрифт
            self.settings_manager.save_font_settings(settings["font_family"], new_size)
            self.apply_font_settings()
        else:
            super().wheelEvent(event)

    async def _start_translation_async(self):
        """Асинхронная часть начала перевода."""
        try:
            model_config = self.get_selected_model_config()
            if model_config.get("streaming", False):
                await self.handle_streaming_translation()
            else:
                await self.handle_regular_translation()
        except asyncio.CancelledError:
            self.translated_text.append("\nПеревод отменен.")
        except Exception as e:
            self.show_error_message(str(e))
        finally:
            self.cancel_button.hide()  # Скрываем кнопку отмены после завершения

    def cancel_translation(self):
        """Отменяет текущий процесс перевода."""
        for task in list(self._translation_tasks):
            if not task.done():
                task.cancel()

    def copy_translation(self):
        """Копирует переведенный текст в буфер обмена."""
        text = self.translated_text.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.hide()  # Скрываем главное окно после копирования
