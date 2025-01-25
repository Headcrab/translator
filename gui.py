import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QToolButton,
    QTextEdit,
    QCheckBox,
    QComboBox,
    QPushButton,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QScrollArea,
)
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtCore import QSize
from hotkeys import register_global_hotkeys, unregister_global_hotkeys
from settings_manager import SettingsManager


# Добавляем стили
STYLE_SHEET = """
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

class AddModelDialog(QDialog):
    """Диалоговое окно для добавления новой модели."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_manager = SettingsManager()

        self.setWindowTitle("Добавить модель")
        self.setGeometry(200, 200, 350, 220)
        self.setStyleSheet(STYLE_SHEET)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Словарь провайдеров и их endpoint'ов
        self.providers = {
            "OpenAI": "https://api.openai.com/v1",
            "Anthropic": "https://api.anthropic.com/",
            "OpenRouter": "https://openrouter.ai/api/v1/chat/completions"
        }

        # Поля ввода
        self.name_edit = QLineEdit(self)
        self.provider_combo = QComboBox(self)
        self.provider_combo.addItems(list(self.providers.keys()))
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        
        self.api_endpoint_edit = QLineEdit(self)
        self.api_endpoint_edit.setText(self.providers[self.provider_combo.currentText()])
        self.model_name_edit = QLineEdit(self)
        self.access_token_edit = QLineEdit(self)

        # Добавляем поля с метками
        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)

        labels = ["Название:", "Провайдер:", "API endpoint:", "Название модели:", "Токен доступа:"]
        widgets = [self.name_edit, self.provider_combo, self.api_endpoint_edit, 
                  self.model_name_edit, self.access_token_edit]

        for label_text, widget in zip(labels, widgets):
            label = QLabel(label_text)
            label.setStyleSheet("color: #444; font-weight: bold;")
            form_layout.addWidget(label)
            form_layout.addWidget(widget)

        layout.addLayout(form_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        ok_button = QPushButton("Добавить", self)
        ok_button.clicked.connect(self.accept)

        cancel_button = QPushButton("Отмена", self)
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def on_provider_changed(self, provider):
        """Обработчик изменения провайдера."""
        self.api_endpoint_edit.setText(self.providers[provider])

    def get_model_data(self):
        """Возвращает данные модели из полей ввода."""
        return {
            "name": self.name_edit.text(),
            "provider": self.provider_combo.currentText(),
            "api_endpoint": self.api_endpoint_edit.text(),
            "model_name": self.model_name_edit.text(),
            "access_token": self.access_token_edit.text(),
        }


class MainWindow(QMainWindow):
    # Сигналы
    clipboard_updated = pyqtSignal(str)
    show_window_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()

        self.setWindowTitle("Мое Python-приложение (PyQt)")
        self.setStyleSheet(STYLE_SHEET)

        # Устанавливаем геометрию из настроек
        x, y, width, height = self.settings_manager.get_window_geometry()
        self.setGeometry(x, y, width, height)

        # Подключение сигналов к слотам
        self.clipboard_updated.connect(self.update_clipboard)
        self.show_window_requested.connect(self.show_window)

        # Создаем верхний виджет для кнопок и комбобоксов
        top_widget = QWidget(self)
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(10, 10, 10, 5)
        top_layout.setSpacing(5)

        # Общий стиль для кнопок
        button_style = """
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

        # Кнопка для открытия окна настроек
        settings_button = QToolButton(self)
        settings_button.setIcon(self.style().standardIcon(self.style().SP_DialogOpenButton))
        settings_button.setIconSize(QSize(20, 20))
        settings_button.setFixedSize(32, 32)
        settings_button.setStyleSheet(button_style)
        settings_button.setToolTip("Настройки")
        settings_button.clicked.connect(self.open_settings)

        # Кнопка для перевода текста
        translate_button = QToolButton(self)
        translate_button.setIcon(self.style().standardIcon(self.style().SP_BrowserReload))
        translate_button.setIconSize(QSize(20, 20))
        translate_button.setFixedSize(32, 32)
        translate_button.setStyleSheet(button_style)
        translate_button.setToolTip("Перевести")
        translate_button.clicked.connect(self.translate_text)

        # Дропбокс выбора языка
        language_label = QLabel("Язык:", self)
        language_label.setStyleSheet("color: #444; font-weight: bold;")
        self.language_combo = QComboBox(self)
        self.language_combo.setMinimumWidth(120)
        available_languages, current_language = self.settings_manager.get_languages()
        self.language_combo.addItems(available_languages)
        self.language_combo.setCurrentText(current_language)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)

        # Дропбокс выбора модели
        model_label = QLabel("Модель:", self)
        model_label.setStyleSheet("color: #444; font-weight: bold;")
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
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
            }
        """)
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
        source_group.setStyleSheet("""
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
        """)
        source_layout = QVBoxLayout(source_group)
        source_layout.setContentsMargins(8, 8, 8, 8)

        self.text_edit = QTextEdit(self)
        self.text_edit.setStyleSheet("""
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
        """)
        source_layout.addWidget(self.text_edit)
        texts_layout.addWidget(source_group)

        # Группа для переведенного текста
        translated_group = QGroupBox("Переведенный текст")
        translated_group.setStyleSheet("""
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
        """)
        translated_layout = QVBoxLayout(translated_group)
        translated_layout.setContentsMargins(8, 8, 8, 8)

        self.translated_text = QTextEdit(self)
        self.translated_text.setStyleSheet("""
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
        """)
        self.translated_text.setReadOnly(True)  # Делаем поле только для чтения
        translated_layout.addWidget(self.translated_text)
        texts_layout.addWidget(translated_group)

        central_layout.addLayout(texts_layout)
        self.setCentralWidget(central_widget)

        self.settings_window = SettingsWindow(self)

        # Проверяем, нужно ли запускать свернутым
        start_minimized, _ = self.settings_manager.get_behavior()
        if start_minimized:
            self.showMinimized()
        else:
            self.show()

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


class SettingsWindow(QDialog):
    """Окно настроек."""

    def __init__(self, main_window):
        self.main_window = main_window
        super().__init__()
        self.settings_manager = SettingsManager()

        self.setWindowTitle("Настройки")
        self.setGeometry(200, 200, 450, 600)
        self.setStyleSheet(STYLE_SHEET)

        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Создаем область прокрутки
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # Создаем контейнер для содержимого
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(8)

        # Группа настроек хоткеев
        hotkey_group = QGroupBox("Горячие клавиши")
        hotkey_layout = QVBoxLayout()
        hotkey_layout.setSpacing(10)

        # Чекбоксы для модификаторов в горизонтальном layout
        modifiers_layout = QHBoxLayout()
        self.ctrl_checkbox = QCheckBox("Ctrl")
        self.shift_checkbox = QCheckBox("Shift")
        self.alt_checkbox = QCheckBox("Alt")
        self.win_checkbox = QCheckBox("Win")

        modifiers_layout.addWidget(self.ctrl_checkbox)
        modifiers_layout.addWidget(self.shift_checkbox)
        modifiers_layout.addWidget(self.alt_checkbox)
        modifiers_layout.addWidget(self.win_checkbox)
        modifiers_layout.addStretch()

        hotkey_layout.addLayout(modifiers_layout)

        # Выпадающий список для клавиши
        key_label = QLabel("Клавиша:")
        key_label.setStyleSheet("color: #444; font-weight: bold;")
        self.key_combobox = QComboBox()
        self.key_combobox.addItems([
            "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
            "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
            "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
            "Esc", "Tab", "Space", "Enter", "Backspace", "Insert", "Delete",
            "Home", "End", "PageUp", "PageDown", "Left", "Right", "Up", "Down"
        ])
        
        hotkey_layout.addWidget(key_label)
        hotkey_layout.addWidget(self.key_combobox)
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)

        # Группа настроек поведения
        behavior_group = QGroupBox("Поведение")
        behavior_layout = QVBoxLayout()
        behavior_layout.setSpacing(10)

        self.start_minimized_checkbox = QCheckBox("Запускать свернутым")
        self.minimize_to_tray_checkbox = QCheckBox("Скрывать в трей при закрытии")

        behavior_layout.addWidget(self.start_minimized_checkbox)
        behavior_layout.addWidget(self.minimize_to_tray_checkbox)
        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)

        # Группа настроек языков
        languages_group = QGroupBox("Языки")
        languages_layout = QVBoxLayout()
        languages_layout.setSpacing(10)

        languages_label = QLabel("Список доступных языков:")
        languages_label.setStyleSheet("color: #444; font-weight: bold;")
        languages_layout.addWidget(languages_label)

        self.languages_edit = QTextEdit()
        self.languages_edit.setMaximumHeight(100)
        available_languages, _ = self.settings_manager.get_languages()
        self.languages_edit.setText("\n".join(available_languages))
        languages_layout.addWidget(self.languages_edit)

        languages_group.setLayout(languages_layout)
        layout.addWidget(languages_group)

        # Группа настроек моделей
        models_group = QGroupBox("Модели")
        models_layout = QVBoxLayout()
        models_layout.setSpacing(10)

        models_label = QLabel("Список моделей:")
        models_label.setStyleSheet("color: #444; font-weight: bold;")
        models_layout.addWidget(models_label)

        self.models_edit = QTextEdit()
        self.models_edit.setMaximumHeight(150)
        self.models_edit.setReadOnly(True)
        models_layout.addWidget(self.models_edit)

        # Кнопки управления моделями
        models_buttons_layout = QHBoxLayout()
        models_buttons_layout.setSpacing(10)

        add_model_button = QPushButton("Добавить")
        add_model_button.clicked.connect(self.add_model)

        remove_model_button = QPushButton("Удалить")
        remove_model_button.clicked.connect(self.remove_model)

        models_buttons_layout.addWidget(add_model_button)
        models_buttons_layout.addWidget(remove_model_button)
        models_buttons_layout.addStretch()

        models_layout.addLayout(models_buttons_layout)
        models_group.setLayout(models_layout)
        layout.addWidget(models_group)

        # Устанавливаем контент в область прокрутки
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Кнопки "Ок" и "Отмена" в горизонтальном layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        ok_button = QPushButton("Ок")
        ok_button.clicked.connect(self.save_settings)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.close)

        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        main_layout.addLayout(buttons_layout)

        self.load_settings()

    def load_settings(self):
        """Загружает настройки."""
        # Загрузка настроек хоткеев
        modifiers, key = self.settings_manager.get_hotkey()

        self.ctrl_checkbox.setChecked("ctrl" in modifiers)
        self.shift_checkbox.setChecked("shift" in modifiers)
        self.alt_checkbox.setChecked("alt" in modifiers)
        self.win_checkbox.setChecked("win" in modifiers)
        self.key_combobox.setCurrentText(key)

        # Загрузка настроек поведения
        start_minimized, minimize_to_tray = self.settings_manager.get_behavior()
        self.start_minimized_checkbox.setChecked(start_minimized)
        self.minimize_to_tray_checkbox.setChecked(minimize_to_tray)

        # Загрузка списка языков
        available_languages, _ = self.settings_manager.get_languages()
        self.languages_edit.setText("\n".join(available_languages))

        # Загрузка списка моделей
        available_models, _ = self.settings_manager.get_models()
        models_text = []
        for model in available_models:
            models_text.append(f"Название: {model['name']}")
            models_text.append(f"Провайдер: {model['provider']}")
            models_text.append(f"API endpoint: {model['api_endpoint']}")
            models_text.append(f"Модель: {model['model_name']}")
            if model.get('access_token'):
                # Показываем только первые и последние 4 символа токена для безопасности
                token = model['access_token']
                masked_token = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "****"
                models_text.append(f"Токен: {masked_token}")
            else:
                models_text.append("Токен: не установлен")
            models_text.append("-" * 30)
        self.models_edit.setText("\n".join(models_text))

    def closeEvent(self, event):
        """Переопределяем поведение при закрытии окна настроек."""
        event.ignore()
        self.hide()

    def save_settings(self):
        """Сохраняет настройки."""
        # Сохранение настроек хоткеев
        modifiers = []
        if self.ctrl_checkbox.isChecked():
            modifiers.append("ctrl")
        if self.shift_checkbox.isChecked():
            modifiers.append("shift")
        if self.alt_checkbox.isChecked():
            modifiers.append("alt")
        if self.win_checkbox.isChecked():
            modifiers.append("win")

        key = self.key_combobox.currentText()
        self.settings_manager.set_hotkey(modifiers, key)

        # Сохранение настроек поведения
        self.settings_manager.set_behavior(
            self.start_minimized_checkbox.isChecked(),
            self.minimize_to_tray_checkbox.isChecked(),
        )

        # Сохранение списка языков
        languages = [
            lang.strip()
            for lang in self.languages_edit.toPlainText().split("\n")
            if lang.strip()
        ]
        self.settings_manager.set_available_languages(languages)

        # Обновляем список языков в главном окне
        self.main_window.language_combo.clear()
        self.main_window.language_combo.addItems(languages)

        # Обновление хоткеев
        unregister_global_hotkeys()
        hotkey_str = "+".join(modifiers) + "+" + key if modifiers else key
        register_global_hotkeys(self.main_window, hotkey_str)

        self.hide()

    def add_model(self):
        """Открывает диалог добавления модели."""
        dialog = AddModelDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            model_data = dialog.get_model_data()

            # Проверяем, что все поля заполнены
            if all(model_data.values()):
                self.settings_manager.add_model(
                    model_data["name"],
                    model_data["provider"],
                    model_data["api_endpoint"],
                    model_data["model_name"],
                    model_data["access_token"],
                )

                # Обновляем список моделей
                self.load_settings()
                self.main_window.update_model_combo()
            else:
                QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены")

    def remove_model(self):
        """Удаляет выбранную модель."""
        available_models, _ = self.settings_manager.get_models()
        if not available_models:
            QMessageBox.warning(self, "Ошибка", "Нет доступных моделей для удаления")
            return

        # Получаем имя текущей выбранной модели
        current_model = self.main_window.model_combo.currentText()
        if current_model:
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите удалить модель '{current_model}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.settings_manager.remove_model(current_model)
                self.load_settings()
                self.main_window.update_model_combo()
