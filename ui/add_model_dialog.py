"""Диалог добавления новой модели."""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QCheckBox,
    QFormLayout,
)
from settings_manager import SettingsManager
from .styles import get_style


class AddModelDialog(QDialog):
    """Диалоговое окно для добавления новой модели."""

    def __init__(self, main_window):
        self.main_window = main_window
        super().__init__(main_window)  # Указываем родительское окно
        self.settings_manager = SettingsManager()

        self.setWindowTitle("Добавить модель")
        self.setFixedSize(400, 360)
        self.center_relative_to_parent()
        self.apply_theme()

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # Словарь провайдеров и их endpoint'ов
        self.providers = {
            "OpenAI": "https://api.openai.com/v1",
            "Anthropic": "https://api.anthropic.com/",
            "OpenRouter": "https://openrouter.ai/api/v1/chat/completions",
        }

        # Поля ввода
        self.name_edit = QLineEdit(self)
        self.provider_combo = QComboBox(self)
        self.provider_combo.addItems(list(self.providers.keys()))
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)

        self.api_endpoint_edit = QLineEdit(self)
        self.api_endpoint_edit.setText(
            self.providers[self.provider_combo.currentText()]
        )
        self.model_name_edit = QLineEdit(self)
        self.access_token_edit = QLineEdit(self)

        # Создаем form_layout с QFormLayout
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(8)

        # Добавляем элементы через addRow
        labels = [
            "Название:", "Провайдер:", "API endpoint:", 
            "Название модели:", "Токен доступа:"
        ]
        widgets = [
            self.name_edit, self.provider_combo, 
            self.api_endpoint_edit, self.model_name_edit, 
            self.access_token_edit
        ]
        
        for label_text, widget in zip(labels, widgets):
            form_layout.addRow(QLabel(label_text), widget)
        
        # Добавляем чекбокс потокового вывода
        self.stream_checkbox = QCheckBox()
        form_layout.addRow("Потоковый вывод:", self.stream_checkbox)
        
        # Добавляем form_layout в основной layout
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

    def apply_theme(self):
        """Применяет текущую тему к окну и всем его элементам."""
        theme_mode = self.settings_manager.get_theme()
        style = get_style(theme_mode)
        self.setStyleSheet(style)
        self.update()

    def on_provider_changed(self, provider):
        """Обработчик изменения провайдера."""
        self.api_endpoint_edit.setText(self.providers[provider])

    def get_model_data(self):
        """Возвращает данные модели из диалога."""
        return {
            "name": self.name_edit.text().strip(),
            "provider": self.provider_combo.currentText().strip(),
            "api_endpoint": self.api_endpoint_edit.text().strip(),
            "model_name": self.model_name_edit.text().strip(),
            "access_token": self.access_token_edit.text().strip(),
            "streaming": self.stream_checkbox.isChecked()
        }

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
