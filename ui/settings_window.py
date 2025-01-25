"""Окно настроек приложения."""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QGroupBox,
    QLabel,
    QCheckBox,
    QComboBox,
    QPushButton,
    QTextEdit,
    QScrollArea,
    QMessageBox,
)
from settings_manager import SettingsManager
from hotkeys import register_global_hotkeys, unregister_global_hotkeys
from .styles import COMMON_STYLE
from .add_model_dialog import AddModelDialog


class SettingsWindow(QDialog):
    """Окно настроек."""

    def __init__(self, main_window):
        self.main_window = main_window
        super().__init__()
        self.settings_manager = SettingsManager()

        self.setWindowTitle("Настройки")
        self.setGeometry(200, 200, 450, 700)
        self.setStyleSheet(COMMON_STYLE)

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
        self.key_combobox.addItems(
            [
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
                "G",
                "H",
                "I",
                "J",
                "K",
                "L",
                "M",
                "N",
                "O",
                "P",
                "Q",
                "R",
                "S",
                "T",
                "U",
                "V",
                "W",
                "X",
                "Y",
                "Z",
                "0",
                "1",
                "2",
                "3",
                "4",
                "5",
                "6",
                "7",
                "8",
                "9",
                "F1",
                "F2",
                "F3",
                "F4",
                "F5",
                "F6",
                "F7",
                "F8",
                "F9",
                "F10",
                "F11",
                "F12",
                "Esc",
                "Tab",
                "Space",
                "Enter",
                "Backspace",
                "Insert",
                "Delete",
                "Home",
                "End",
                "PageUp",
                "PageDown",
                "Left",
                "Right",
                "Up",
                "Down",
            ]
        )

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
            if model.get("access_token"):
                # Показываем только первые и последние 4 символа токена для безопасности
                token = model["access_token"]
                masked_token = (
                    f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "****"
                )
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
