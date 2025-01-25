"""Диалог добавления новой модели."""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
)
from settings_manager import SettingsManager
from .styles import COMMON_STYLE


class AddModelDialog(QDialog):
    """Диалоговое окно для добавления новой модели."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_manager = SettingsManager()

        self.setWindowTitle("Добавить модель")
        self.setGeometry(200, 200, 350, 220)
        self.setStyleSheet(COMMON_STYLE)

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

        # Добавляем поля с метками
        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)

        labels = [
            "Название:",
            "Провайдер:",
            "API endpoint:",
            "Название модели:",
            "Токен доступа:",
        ]
        widgets = [
            self.name_edit,
            self.provider_combo,
            self.api_endpoint_edit,
            self.model_name_edit,
            self.access_token_edit,
        ]

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
