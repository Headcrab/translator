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
    QMessageBox,
    QListWidget,
    QLineEdit,
    QToolButton,
    QTabWidget,
    QFontComboBox,
    QFormLayout,
)
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtCore import Qt
from settings_manager import SettingsManager
from .styles import get_style
from .add_model_dialog import AddModelDialog
from .add_prompt_dialog import AddPromptDialog


class SettingsWindow(QDialog):
    """Окно настроек."""

    def __init__(self, parent=None):
        """Инициализация окна настроек."""
        super().__init__(parent)
        self.settings_manager = SettingsManager()
        self.layout = QFormLayout()  # Инициализируем QFormLayout для работы с addRow
        
        # Устанавливаем фиксированные размеры окна
        self.setMinimumWidth(400)  # Увеличиваем минимальную ширину
        self.setMinimumHeight(600)  # Устанавливаем минимальную высоту
        
        # Восстановление геометрии или установка по умолчанию
        x, y, w, h = self.settings_manager.get_settings_window_geometry()
        w = max(w, 400)  # Убеждаемся, что ширина не меньше минимальной
        h = max(h, 600)  # Убеждаемся, что высота не меньше минимальной
        
        # Центрируем окно относительно родителя
        if parent:
            parent_center = parent.geometry().center()
            x = parent_center.x() - w // 2
            y = parent_center.y() - h // 2
        
        self.setGeometry(x, y, w, h)
        
        self.setWindowTitle("Настройки")
        # self.apply_theme()
        self.center_relative_to_parent()

        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        # self.apply_theme()
        main_layout.addLayout(self.layout)  # Добавляем form layout в основной

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
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(8)

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
        content_layout.addWidget(hotkey_group)

        # Группа настроек поведения
        behavior_group = QGroupBox("Поведение")
        behavior_layout = QVBoxLayout()
        behavior_layout.setSpacing(10)

        self.start_minimized_checkbox = QCheckBox("Запускать свернутым")
        self.minimize_to_tray_checkbox = QCheckBox("Скрывать в трей при закрытии")

        behavior_layout.addWidget(self.start_minimized_checkbox)
        behavior_layout.addWidget(self.minimize_to_tray_checkbox)
        behavior_group.setLayout(behavior_layout)
        system_layout.addWidget(behavior_group)

        # Добавляем секцию шрифтов
        font_group = QGroupBox("Настройки шрифта")
        font_layout = QFormLayout()
        font_label = QLabel("Шрифт текста:")
        self.font_combo = QFontComboBox()
        self.size_combo = QComboBox()
        # Заполняем размеры с проверкой на пустые значения
        sizes = [str(s) for s in range(8, 25) if s > 0]
        self.size_combo.addItems(sizes)

        font_layout.addRow(font_label, self.font_combo)
        font_layout.addRow(QLabel("Размер шрифта:"), self.size_combo)
        font_group.setLayout(font_layout)
        system_layout.addWidget(font_group)

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
        content_layout.addWidget(appearance_group)

        # Группа настроек языков
        languages_group = QGroupBox("Языки")
        languages_layout = QVBoxLayout()
        languages_layout.setSpacing(10)

        # languages_label = QLabel("Список доступных языков:")
        # languages_label.setStyleSheet("color: #444; font-weight: bold;")
        # languages_layout.addWidget(languages_label)

        # Список языков
        self.languages_list = QListWidget()
        self.languages_list.setMaximumHeight(150)
        available_languages, _ = self.settings_manager.get_languages()
        self.languages_list.addItems(available_languages)
        self.languages_list.itemClicked.connect(lambda item: self.language_edit.setText(item.text()))
        
        # Получаем текущий язык из главного окна
        if self.parent():
            current_language = self.parent().language_combo.currentText()
            # Выделяем текущий язык в списке
            for i in range(self.languages_list.count()):
                if self.languages_list.item(i).text() == current_language:
                    self.languages_list.setCurrentRow(i)
                    break

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
        content_layout.addWidget(languages_group)

        # Группа настроек моделей
        models_group = QGroupBox("Модели")
        models_layout = QVBoxLayout()
        models_layout.setSpacing(10)

        # models_label = QLabel("Список моделей:")
        # models_label.setStyleSheet("color: #444; font-weight: bold;")
        # models_layout.addWidget(models_label)

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
        content_layout.addWidget(models_group)

        # Группа настроек системных промптов
        prompts_group = QGroupBox("Системные промпты")
        prompts_layout = QVBoxLayout()
        prompts_layout.setSpacing(10)

        # prompts_label = QLabel("Список промптов:")
        # prompts_label.setStyleSheet("color: #444; font-weight: bold;")
        # prompts_layout.addWidget(prompts_label)

        # Список промптов
        self.prompts_list = QListWidget()
        self.prompts_list.setMaximumHeight(150)
        self.prompts_list.itemDoubleClicked.connect(self.edit_prompt)
        prompts_layout.addWidget(self.prompts_list)
        
        # Получаем текущий промпт из главного окна
        if self.parent():
            current_prompt = self.parent().prompt_combo.currentText()
            # Выделяем текущий промпт в списке
            for i in range(self.prompts_list.count()):
                if self.prompts_list.item(i).text() == current_prompt:
                    self.prompts_list.setCurrentRow(i)
                    break

        # Создаем горизонтальный layout для кнопок управления промптами
        prompts_input_layout = QHBoxLayout()
        prompts_input_layout.setSpacing(5)

        # Кнопки управления промптами
        self.add_prompt_btn = QToolButton()
        self.add_prompt_btn.setIcon(self.style().standardIcon(self.style().SP_FileIcon))
        self.add_prompt_btn.setToolTip("Добавить промпт")
        self.add_prompt_btn.setFixedHeight(button_height)
        self.add_prompt_btn.clicked.connect(self.add_prompt)

        self.edit_prompt_btn = QToolButton()
        self.edit_prompt_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
        self.edit_prompt_btn.setToolTip("Редактировать промпт")
        self.edit_prompt_btn.setFixedHeight(button_height)
        self.edit_prompt_btn.clicked.connect(self.edit_prompt)

        self.delete_prompt_btn = QToolButton()
        self.delete_prompt_btn.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        self.delete_prompt_btn.setToolTip("Удалить промпт")
        self.delete_prompt_btn.setFixedHeight(button_height)
        self.delete_prompt_btn.clicked.connect(self.delete_prompt)

        prompts_input_layout.addStretch()
        prompts_input_layout.addWidget(self.add_prompt_btn)
        prompts_input_layout.addWidget(self.edit_prompt_btn)
        prompts_input_layout.addWidget(self.delete_prompt_btn)

        prompts_layout.addLayout(prompts_input_layout)
        prompts_group.setLayout(prompts_layout)
        content_layout.addWidget(prompts_group)

        # Распределяем группы по вкладкам
        
        # Вкладка "Общие"
        general_layout.addWidget(languages_group)
        general_layout.addWidget(models_group)
        general_layout.addWidget(prompts_group)
        general_layout.addStretch()
        
        # Вкладка "Системные"
        system_layout.addWidget(hotkey_group)
        system_layout.addWidget(appearance_group)
        system_layout.addWidget(behavior_group)
        system_layout.addWidget(font_group)
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

        # Создаем все элементы интерфейса
        self._init_ui_components()
        
        # Загружаем настройки после создания всех компонентов
        self.load_settings()
        self.apply_theme()

        # Настраиваем обработку клавиш для списков
        self.languages_list.keyPressEvent = lambda event: self.handle_list_key_event(event, self.languages_list)
        self.models_list.keyPressEvent = lambda event: self.handle_list_key_event(event, self.models_list)
        self.prompts_list.keyPressEvent = lambda event: self.handle_list_key_event(event, self.prompts_list)

    def _init_ui_components(self):
        """Инициализация компонентов интерфейса."""
        # Удалите или закомментируйте следующие строки:
        # self.font_combo = QFontComboBox()
        # self.size_combo = QComboBox()
        
        # Инициализация комбобоксов шрифта
        self.size_combo.clear()
        sizes = [str(s) for s in range(8, 25)]
        self.size_combo.addItems(sizes)

    def apply_theme(self):
        """Применяет текущую тему к окну и всем его элементам."""
        theme_mode = self.settings_manager.get_theme()
        style = get_style(theme_mode)
        
        # Применяем стили ко всему окну и его элементам
        self.setStyleSheet(style)
        
        # Стилизация вкладок
        if hasattr(self, 'tab_widget'):
            from ui.styles import get_tab_style
            tab_style = get_tab_style(theme_mode)
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
        
        # Получаем текущий язык из главного окна
        if self.parent():
            current_language = self.parent().language_combo.currentText()
            # Выделяем текущий язык в списке
            for i in range(self.languages_list.count()):
                if self.languages_list.item(i).text() == current_language:
                    self.languages_list.setCurrentRow(i)
                    break

        # Загрузка списка моделей
        available_models, _ = self.settings_manager.get_models()
        self.models_list.clear()
        
        # Добавляем модели в список
        for model in available_models:
            self.models_list.addItem(model["name"])
        
        # Получаем текущую модель из главного окна
        if self.parent():
            current_model_name = self.parent().model_combo.currentText()
            # Выделяем текущую модель в списке
            for i in range(self.models_list.count()):
                if self.models_list.item(i).text() == current_model_name:
                    self.models_list.setCurrentRow(i)
                    break

        # Загрузка списка промптов
        available_prompts, _ = self.settings_manager.get_prompts()
        self.prompts_list.clear()
        
        # Добавляем промпты в список
        for prompt in available_prompts:
            self.prompts_list.addItem(prompt["name"])
        
        # Получаем текущий промпт из главного окна
        if self.parent():
            current_prompt = self.parent().prompt_combo.currentText()
            # Выделяем текущий промпт в списке
            for i in range(self.prompts_list.count()):
                if self.prompts_list.item(i).text() == current_prompt:
                    self.prompts_list.setCurrentRow(i)
                    break

        # Загрузка настроек шрифта
        font_settings = self.settings_manager.get_font_settings()
        
        # Устанавливаем шрифт
        font = QFont(font_settings["font_family"])
        self.font_combo.setCurrentFont(font)
        
        # Устанавливаем размер
        size_str = str(font_settings["font_size"])
        index = self.size_combo.findText(size_str)
        if index >= 0:
            self.size_combo.setCurrentIndex(index)
        else:
            # Если размер не найден в списке, добавляем его
            self.size_combo.addItem(size_str)
            self.size_combo.setCurrentText(size_str)

    def closeEvent(self, event):
        """Переопределяем поведение при закрытии окна настроек."""
        # Сохраняем все настройки перед закрытием
        self.save_settings()
        
        # Сохранение геометрии
        geom = self.geometry()
        self.settings_manager.set_settings_window_geometry(
            geom.x(), geom.y(), geom.width(), geom.height()
        )
        super().closeEvent(event)

    def save_settings(self):
        """Сохраняет настройки."""
        # Сохранение настроек шрифта
        font_family = self.font_combo.currentFont().family()
        font_size = int(self.size_combo.currentText())
        self.settings_manager.save_font_settings(font_family, font_size)
        
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

        # Применяем новые настройки шрифта к родительскому окну
        parent = self.parent()
        if hasattr(parent, 'apply_font_settings'):
            parent.apply_font_settings()

        # Добавляю обновление текущей модели из списка настроек
        selected_item = self.models_list.currentItem()
        if selected_item:
            model_name = selected_item.text()
            self.settings_manager.set_current_model(model_name)
            
            # Обновляем модель в главном окне
            if self.parent():
                index = self.parent().model_combo.findText(model_name)
                if index >= 0:
                    self.parent().model_combo.setCurrentIndex(index)

        # Добавляю обновление текущего языка из списка
        selected_lang = self.languages_list.currentItem()
        if selected_lang:
            lang_name = selected_lang.text()
            self.settings_manager.set_current_language(lang_name)
            
            # Обновляем язык в главном окне
            if self.parent():
                index = self.parent().language_combo.findText(lang_name)
                if index >= 0:
                    self.parent().language_combo.setCurrentIndex(index)

        # Добавляю обновление текущего промпта из списка
        selected_prompt = self.prompts_list.currentItem()
        if selected_prompt:
            prompt_name = selected_prompt.text()
            self.settings_manager.set_current_prompt(prompt_name)
            
            # Обновляем промпт в главном окне
            if self.parent():
                index = self.parent().prompt_combo.findText(prompt_name)
                if index >= 0:
                    self.parent().prompt_combo.setCurrentIndex(index)

        self.hide()
        
        # Обновляем тему в главном окне
        if self.parent():
            self.parent().apply_theme()

    def add_model(self):
        """Открывает диалог добавления новой модели."""
        dialog = AddModelDialog(self)
        dialog.center_relative_to_parent()
        dialog.apply_theme()
        
        # Добавляем обработчики событий для автоматического обновления названия
        dialog.provider_combo.currentTextChanged.connect(
            lambda: self.update_model_name(dialog)
        )
        dialog.model_name_edit.currentTextChanged.connect(
            lambda: self.update_model_name(dialog)
        )
        
        if dialog.exec_() == QDialog.Accepted:
            model_data = dialog.get_model_info()
            if model_data:
                self.settings_manager.add_model(
                    name=model_data["name"],
                    provider=model_data["provider"],
                    api_endpoint=model_data["api_endpoint"],
                    model_name=model_data["model_name"],
                    access_token="",
                    access_token_env=model_data["access_token_env"],
                    streaming=model_data["streaming"]
                )
                self.update_models_list()

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
                # Получаем текущий список моделей
                available_models, _ = self.settings_manager.get_models()
                # Находим модель по отображаемому имени
                for model in available_models:
                    if model["name"] == model_name:
                        self.settings_manager.remove_model(model['name'])
                        break
                
                self.load_settings()
                # Обновляем список моделей в главном окне через родительское окно
                self.parent().update_model_combo()

    def add_language(self):
        """Добавляет новый язык."""
        language = self.language_edit.text().strip()
        if language:
            self.settings_manager.add_language(language)
            self.load_settings()
            self.language_edit.clear()
            # Обновляем список языков через родительское окно
            self.parent().language_combo.clear()
            available_languages, _ = self.settings_manager.get_languages()
            self.parent().language_combo.addItems(available_languages)

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
                # Обновляем список языков через родительское окно
                self.parent().language_combo.clear()
                available_languages, _ = self.settings_manager.get_languages()
                self.parent().language_combo.addItems(available_languages)

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
                # Обновляем список языков через родительское окно
                self.parent().language_combo.clear()
                available_languages, _ = self.settings_manager.get_languages()
                self.parent().language_combo.addItems(available_languages)

    def edit_model(self):
        """Редактирует выбранную модель."""
        selected = self.models_list.currentItem()
        if selected:
            display_name = selected.text()
            current_position = self.models_list.currentRow()
            available_models, _ = self.settings_manager.get_models()
            
            # Находим модель по отображаемому имени
            current_model = next(
                (model for model in available_models 
                if model["name"] == display_name),
                None
            )
            
            if current_model:
                dialog = AddModelDialog(self)
                dialog.center_relative_to_parent()
                dialog.apply_theme()
                
                # Заполняем диалог текущими данными модели
                dialog.name_edit.setText(current_model['name'])
                dialog.provider_combo.setCurrentText(current_model['provider'])
                
                # Устанавливаем endpoint и API key
                dialog.api_endpoint_edit.setText(current_model.get('api_endpoint', ''))
                # Используем access_token_env если он есть
                dialog.api_key_edit.setText(current_model.get('access_token_env', ''))
                
                # Добавляем текущую модель в комбобокс и выбираем её
                dialog.model_name_edit.clear()
                dialog.model_name_edit.addItem(current_model['model_name'])
                dialog.model_name_edit.setCurrentText(current_model['model_name'])
                
                dialog.stream_checkbox.setChecked(current_model.get('streaming', False))
                
                # Добавляем обработчики событий для автоматического обновления названия
                dialog.provider_combo.currentTextChanged.connect(
                    lambda: self.update_model_name(dialog)
                )
                dialog.model_name_edit.currentTextChanged.connect(
                    lambda: self.update_model_name(dialog)
                )
                
                if dialog.exec_() == QDialog.Accepted:
                    model_data = dialog.get_model_info()
                    if model_data:
                        # Получаем текущий список моделей
                        available_models, _ = self.settings_manager.get_models()
                        # Удаляем старую модель из списка
                        available_models = [m for m in available_models if m['name'] != current_model['name']]
                        
                        # Вставляем новую модель на ту же позицию
                        available_models.insert(current_position, {
                            'name': model_data["name"],
                            'provider': model_data["provider"],
                            'api_endpoint': model_data["api_endpoint"],
                            'model_name': model_data["model_name"],
                            'access_token': "",
                            'access_token_env': model_data["access_token_env"],
                            'streaming': model_data["streaming"]
                        })
                        
                        # Обновляем список в settings_manager
                        self.settings_manager.settings['models']['available'] = available_models
                        self.settings_manager.save_settings()
                        
                        # Обновляем интерфейс
                        self.load_settings()
                        if self.parent():
                            self.parent().update_model_combo()
                        
                        # Восстанавливаем выделение на отредактированной модели
                        self.models_list.setCurrentRow(current_position)

    def update_model_name(self, dialog):
        """Обновляет название модели на основе провайдера и имени модели."""
        provider = dialog.provider_combo.currentText()
        model_name = dialog.model_name_edit.currentText()
        
        if provider and model_name:
            # Формируем название в формате: Model - Provider
            new_name = f"{model_name} - {provider}"
            dialog.name_edit.setText(new_name)

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

    def update_models_list(self):
        """Обновляет список моделей в интерфейсе."""
        self.load_settings()  # Перезагружаем все настройки
        if self.parent():
            self.parent().update_model_combo()  # Обновляем список в главном окне

    def handle_list_key_event(self, event: QKeyEvent, list_widget: QListWidget):
        """Обработка нажатий клавиш для списков."""
        if event.modifiers() == Qt.AltModifier:
            current_row = list_widget.currentRow()
            if current_row == -1:  # Нет выбранного элемента
                return super(QListWidget, list_widget).keyPressEvent(event)
                
            if event.key() == Qt.Key_Up and current_row > 0:
                # Перемещаем элемент вверх
                item = list_widget.takeItem(current_row)
                list_widget.insertItem(current_row - 1, item)
                list_widget.setCurrentRow(current_row - 1)
                self.save_list_order(list_widget)
                
            elif event.key() == Qt.Key_Down and current_row < list_widget.count() - 1:
                # Перемещаем элемент вниз
                item = list_widget.takeItem(current_row)
                list_widget.insertItem(current_row + 1, item)
                list_widget.setCurrentRow(current_row + 1)
                self.save_list_order(list_widget)
                
            else:
                super(QListWidget, list_widget).keyPressEvent(event)
        else:
            super(QListWidget, list_widget).keyPressEvent(event)

    def save_list_order(self, list_widget: QListWidget):
        """Сохраняет новый порядок элементов в настройках."""
        items = [list_widget.item(i).text() for i in range(list_widget.count())]
        
        if list_widget == self.languages_list:
            # Сохраняем порядок языков
            self.settings_manager.set_available_languages(items)
            # Обновляем список языков в главном окне
            if self.parent():
                self.parent().language_combo.clear()
                self.parent().language_combo.addItems(items)
        
        elif list_widget == self.models_list:
            # Сохраняем порядок моделей
            available_models, _ = self.settings_manager.get_models()
            # Создаем новый список моделей в нужном порядке
            reordered_models = []
            for name in items:
                for model in available_models:
                    if model['name'] == name:
                        reordered_models.append(model)
                        break
            
            # Обновляем порядок в settings_manager
            self.settings_manager.settings['models']['available'] = reordered_models
            self.settings_manager.save_settings()
            
            # Обновляем список моделей в главном окне
            if self.parent():
                self.parent().update_model_combo()
        
        elif list_widget == self.prompts_list:
            # Сохраняем порядок промптов
            available_prompts, _ = self.settings_manager.get_prompts()
            # Создаем новый список промптов в нужном порядке
            reordered_prompts = []
            for name in items:
                for prompt in available_prompts:
                    if prompt['name'] == name:
                        reordered_prompts.append(prompt)
                        break
            
            # Обновляем порядок в settings_manager
            self.settings_manager.settings['prompts']['available'] = reordered_prompts
            self.settings_manager.save_settings()
            
            # Обновляем список промптов в главном окне
            if self.parent():
                self.parent().update_prompt_combo()

    def edit_prompt(self):
        """Редактирует выбранный системный промпт."""
        selected = self.prompts_list.currentItem()
        if selected:
            # Получаем информацию о текущем промпте
            prompts, _ = self.settings_manager.get_prompts()
            current_prompt = None
            for prompt in prompts:
                if prompt["name"] == selected.text():
                    current_prompt = prompt
                    break
            
            if current_prompt:
                dialog = AddPromptDialog(self, current_prompt)
                dialog.center_relative_to_parent()
                dialog.apply_theme()
                
                if dialog.exec_() == QDialog.Accepted:
                    prompt_info = dialog.get_prompt_info()
                    if prompt_info:
                        self.settings_manager.edit_prompt(
                            current_prompt["name"],
                            prompt_info["name"],
                            prompt_info["text"]
                        )
                        self.load_settings()
                        # Обновляем список промптов в главном окне
                        if self.parent():
                            self.parent().update_prompt_combo()

    def delete_prompt(self):
        """Удаляет выбранный системный промпт."""
        selected = self.prompts_list.currentItem()
        if selected:
            name = selected.text()
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                f"Вы уверены, что хотите удалить промпт '{name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.settings_manager.delete_prompt(name)
                self.load_settings()
                # Обновляем список промптов в главном окне
                if self.parent():
                    self.parent().update_prompt_combo()

    def add_prompt(self):
        """Добавляет новый системный промпт."""
        dialog = AddPromptDialog(self)
        dialog.center_relative_to_parent()
        dialog.apply_theme()
        
        if dialog.exec_() == QDialog.Accepted:
            prompt_info = dialog.get_prompt_info()
            if prompt_info:
                self.settings_manager.add_prompt(prompt_info["name"], prompt_info["text"])
                self.load_settings()
                # Обновляем список промптов в главном окне
                if self.parent():
                    self.parent().update_prompt_combo()