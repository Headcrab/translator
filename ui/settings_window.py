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
    QListWidget,
    QLineEdit,
    QToolButton,
    QTabWidget,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from settings_manager import SettingsManager
from hotkeys import register_global_hotkeys, unregister_global_hotkeys
from .styles import get_style
from .add_model_dialog import AddModelDialog


class SettingsWindow(QDialog):
    """Окно настроек."""

    def __init__(self, main_window):
        self.main_window = main_window
        super().__init__(main_window)  # Указываем родительское окно
        self.settings_manager = SettingsManager()

        self.setWindowTitle("Настройки")
        self.setGeometry(200, 200, 450, 500)
        self.center_relative_to_parent()
        self.apply_theme()

        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        self.apply_theme()
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Создаем виджет вкладок
        self.tab_widget = QTabWidget()
        
        # Создаем вкладки
        general_tab = QWidget()
        system_tab = QWidget()
        
        # Создаем layouts для вкладок
        general_layout = QVBoxLayout(general_tab)
        system_layout = QVBoxLayout(system_tab)
        
        # Создаем контент для вкладок
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
        # Группа настроек внешнего вида
        appearance_group = QGroupBox("Внешний вид")
        appearance_layout = QVBoxLayout()
        appearance_layout.setSpacing(10)

        # Настройка темы
        theme_label = QLabel("Тема:")
        theme_label.setStyleSheet("color: #444; font-weight: bold;")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Системная", "Светлая", "Темная"])
        
        appearance_layout.addWidget(theme_label)
        appearance_layout.addWidget(self.theme_combo)
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)

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

        # Список языков
        self.languages_list = QListWidget()
        self.languages_list.setMaximumHeight(150)
        available_languages, _ = self.settings_manager.get_languages()
        self.languages_list.addItems(available_languages)
        self.languages_list.itemClicked.connect(lambda item: self.language_edit.setText(item.text()))
        languages_layout.addWidget(self.languages_list)

        # Создаем горизонтальный layout для поля ввода и кнопок
        lang_input_layout = QHBoxLayout()
        lang_input_layout.setSpacing(5)

        # Поле для редактирования языка
        self.language_edit = QLineEdit()
        self.language_edit.setPlaceholderText("Введите название языка")
        
        # Устанавливаем минимальную высоту для кнопок равной высоте QLineEdit
        button_height = self.language_edit.sizeHint().height()
        
        # Кнопки управления языками
        # Кнопка добавления
        self.add_lang_btn = QToolButton()
        self.add_lang_btn.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
        self.add_lang_btn.setToolTip("Добавить язык")
        self.add_lang_btn.setFixedHeight(button_height)
        self.add_lang_btn.clicked.connect(self.add_language)

        # Кнопка редактирования
        self.edit_lang_btn = QToolButton()
        self.edit_lang_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
        self.edit_lang_btn.setToolTip("Редактировать язык")
        self.edit_lang_btn.setFixedHeight(button_height)
        self.edit_lang_btn.clicked.connect(self.edit_language)

        # Кнопка удаления
        self.delete_lang_btn = QToolButton()
        self.delete_lang_btn.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        self.delete_lang_btn.setToolTip("Удалить язык")
        self.delete_lang_btn.setFixedHeight(button_height)
        self.delete_lang_btn.clicked.connect(self.delete_language)

        # Добавляем элементы в горизонтальный layout
        lang_input_layout.addWidget(self.language_edit)
        lang_input_layout.addWidget(self.add_lang_btn)
        lang_input_layout.addWidget(self.edit_lang_btn)
        lang_input_layout.addWidget(self.delete_lang_btn)

        # Добавляем горизонтальный layout в основной layout языков
        languages_layout.addLayout(lang_input_layout)
        languages_group.setLayout(languages_layout)
        layout.addWidget(languages_group)

        # Группа настроек моделей
        models_group = QGroupBox("Модели")
        models_layout = QVBoxLayout()
        models_layout.setSpacing(10)

        models_label = QLabel("Список моделей:")
        models_label.setStyleSheet("color: #444; font-weight: bold;")
        models_layout.addWidget(models_label)

        # Список моделей
        self.models_list = QListWidget()
        self.models_list.setMaximumHeight(150)
        self.models_list.itemDoubleClicked.connect(self.edit_model)
        models_layout.addWidget(self.models_list)

        # Создаем горизонтальный layout для кнопок управления моделями
        models_input_layout = QHBoxLayout()
        models_input_layout.setSpacing(5)

        # Кнопки управления моделями
        button_height = self.language_edit.sizeHint().height()

        # Кнопка добавления
        self.add_model_btn = QToolButton()
        self.add_model_btn.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
        self.add_model_btn.setToolTip("Добавить модель")
        self.add_model_btn.setFixedHeight(button_height)
        self.add_model_btn.clicked.connect(self.add_model)

        # Кнопка редактирования
        self.edit_model_btn = QToolButton()
        self.edit_model_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
        self.edit_model_btn.setToolTip("Редактировать модель")
        self.edit_model_btn.setFixedHeight(button_height)
        self.edit_model_btn.clicked.connect(self.edit_model)

        # Кнопка удаления
        self.delete_model_btn = QToolButton()
        self.delete_model_btn.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        self.delete_model_btn.setToolTip("Удалить модель")
        self.delete_model_btn.setFixedHeight(button_height)
        self.delete_model_btn.clicked.connect(self.remove_model)

        # Добавляем кнопки в горизонтальный layout
        models_input_layout.addStretch()
        models_input_layout.addWidget(self.add_model_btn)
        models_input_layout.addWidget(self.edit_model_btn)
        models_input_layout.addWidget(self.delete_model_btn)

        models_layout.addLayout(models_input_layout)
        models_group.setLayout(models_layout)
        layout.addWidget(models_group)

        # Распределяем группы по вкладкам
        
        # Вкладка "Общие"
        general_layout.addWidget(languages_group)
        general_layout.addWidget(models_group)
        general_layout.addStretch()
        
        # Вкладка "Системные"
        system_layout.addWidget(hotkey_group)
        system_layout.addWidget(appearance_group)
        system_layout.addWidget(behavior_group)
        system_layout.addStretch()
        
        # Добавляем вкладки в виджет вкладок
        self.tab_widget.addTab(general_tab, "Общие")
        self.tab_widget.addTab(system_tab, "Системные")
        
        # Добавляем виджет вкладок в основной layout
        main_layout.addWidget(self.tab_widget)

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
        self.apply_theme()

    def apply_theme(self):
        """Применяет текущую тему к окну и всем его элементам."""
        theme_mode = self.settings_manager.get_theme()
        style = get_style(theme_mode)
        
        # Применяем стили ко всему окну и его элементам
        self.setStyleSheet(style)
        
        # Стилизация вкладок
        if hasattr(self, 'tab_widget'):
            if theme_mode == "dark":
                tab_style = """
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
                tab_style = """
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
                tab_style = """
                    QTabWidget::tab-bar {
                        left: 5px;
                    }
                    QTabBar::tab {
                        padding: 8px 12px;
                        margin-right: 2px;
                    }
                """
            
            self.tab_widget.setStyleSheet(tab_style)
        
        # Обновляем все элементы, которые могут требовать перерисовки
        self.update()

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

        # Загрузка настроек темы
        theme_mode = self.settings_manager.get_theme()
        theme_index = {
            "system": 0,
            "light": 1,
            "dark": 2
        }.get(theme_mode, 0)
        self.theme_combo.setCurrentIndex(theme_index)

        # Загрузка списка языков
        available_languages, _ = self.settings_manager.get_languages()
        self.languages_list.clear()
        self.languages_list.addItems(available_languages)
        self.language_edit.setText("")

        # Загрузка списка моделей
        available_models, _ = self.settings_manager.get_models()
        self.models_list.clear()
        for model in available_models:
            self.models_list.addItem(model['name'])

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

        # Сохранение настроек темы
        theme_mode = {
            0: "system",
            1: "light",
            2: "dark"
        }.get(self.theme_combo.currentIndex(), "system")
        self.settings_manager.set_theme(theme_mode)

        # Применяем новую тему
        self.apply_theme()
        # Применяем тему к главному окну
        self.main_window.setStyleSheet(get_style(theme_mode))

        # Сохранение списка языков
        languages = []
        for i in range(self.languages_list.count()):
            languages.append(self.languages_list.item(i).text().strip())
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
        selected = self.models_list.currentItem()
        if selected:
            model_name = selected.text()
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите удалить модель '{model_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.settings_manager.remove_model(model_name)
                self.load_settings()
                # Обновляем список моделей в главном окне
                self.main_window.update_model_combo()

    def add_language(self):
        """Добавляет новый язык."""
        language = self.language_edit.text().strip()
        if language:
            self.settings_manager.add_language(language)
            self.load_settings()
            self.language_edit.clear()
            # Обновляем список языков в главном окне
            self.main_window.language_combo.clear()
            available_languages, _ = self.settings_manager.get_languages()
            self.main_window.language_combo.addItems(available_languages)

    def edit_language(self):
        """Редактирует выбранный язык."""
        selected = self.languages_list.currentItem()
        if selected:
            current_language = selected.text()
            new_language = self.language_edit.text().strip()
            if new_language:
                self.settings_manager.edit_language(current_language, new_language)
                self.load_settings()
                self.language_edit.clear()
                # Обновляем список языков в главном окне
                self.main_window.language_combo.clear()
                available_languages, _ = self.settings_manager.get_languages()
                self.main_window.language_combo.addItems(available_languages)

    def delete_language(self):
        """Удаляет выбранный язык."""
        selected = self.languages_list.currentItem()
        if selected:
            language = selected.text()
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите удалить язык '{language}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.settings_manager.delete_language(language)
                self.load_settings()
                self.languages_list.takeItem(self.languages_list.currentRow())
                # Обновляем список языков в главном окне
                self.main_window.language_combo.clear()
                available_languages, _ = self.settings_manager.get_languages()
                self.main_window.language_combo.addItems(available_languages)

    def edit_model(self):
        """Редактирует выбранную модель."""
        selected = self.models_list.currentItem()
        if selected:
            current_model_name = selected.text()
            # Получаем текущие данные модели
            available_models, _ = self.settings_manager.get_models()
            current_model = next((model for model in available_models if model['name'] == current_model_name), None)
            
            if current_model:
                dialog = AddModelDialog(self)
                # Заполняем диалог текущими данными модели
                dialog.name_edit.setText(current_model['name'])
                dialog.provider_combo.setCurrentText(current_model['provider'])
                dialog.api_endpoint_edit.setText(current_model['api_endpoint'])
                dialog.model_name_edit.setText(current_model['model_name'])
                dialog.access_token_edit.setText(current_model.get('access_token', ''))
                
                if dialog.exec_() == QDialog.Accepted:
                    model_data = dialog.get_model_data()
                    if all(model_data.values()):
                        # Удаляем старую модель
                        self.settings_manager.remove_model(current_model_name)
                        # Добавляем новую модель
                        self.settings_manager.add_model(
                            model_data["name"],
                            model_data["provider"],
                            model_data["api_endpoint"],
                            model_data["model_name"],
                            model_data["access_token"],
                        )
                        self.load_settings()
                        # Обновляем список моделей в главном окне
                        self.main_window.update_model_combo()

    def center_relative_to_parent(self):
        """Центрирует окно относительно родительского окна."""
        if self.parent():
            parent_geometry = self.parent().geometry()
            parent_center = parent_geometry.center()
            
            # Получаем размеры текущего окна
            size = self.geometry()
            
            # Вычисляем позицию для центрирования
            x = parent_center.x() - size.width() // 2
            y = parent_center.y() - size.height() // 2
            
            # Перемещаем окно
            self.move(x, y)
