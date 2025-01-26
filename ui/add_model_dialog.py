"""Диалог добавления новой модели."""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QFormLayout,
    QDialogButtonBox,
)
from PyQt5.QtCore import Qt
from settings_manager import SettingsManager
from .styles import get_style
from typing import Dict


class AddModelDialog(QDialog):
    """Диалоговое окно для добавления новой модели."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_manager = SettingsManager()
        
        self.setWindowTitle("Добавить модель")
        
        layout = QVBoxLayout()
        
        # Поля ввода
        self.name_edit = QLineEdit()
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "OpenAI",
            "Anthropic", 
            "Google",
            "OpenRouter"
        ])
        
        self.model_name_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.api_endpoint_edit = QLineEdit()
        self.stream_checkbox = QCheckBox("Использовать потоковый режим")
        
        # Добавляем поля в layout
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Провайдер:", self.provider_combo)
        form_layout.addRow("Модель:", self.model_name_edit)
        form_layout.addRow("API ключ:", self.api_key_edit)
        form_layout.addRow("API endpoint:", self.api_endpoint_edit)
        form_layout.addRow(self.stream_checkbox)
        
        layout.addLayout(form_layout)
        
        # Подсказки для разных провайдеров
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def on_provider_changed(self, provider: str):
        """Обновляет подсказки в зависимости от выбранного провайдера."""
        if provider == "OpenAI":
            self.model_name_edit.setPlaceholderText("gpt-3.5-turbo")
            self.api_endpoint_edit.setPlaceholderText("https://api.openai.com/v1")
        elif provider == "Anthropic":
            self.model_name_edit.setPlaceholderText("claude-2")
            self.api_endpoint_edit.setPlaceholderText("https://api.anthropic.com")
        elif provider == "Google":
            self.model_name_edit.setPlaceholderText("gemini-pro")
            self.api_endpoint_edit.setPlaceholderText("Оставьте пустым для Google AI")
        elif provider == "OpenRouter":
            self.model_name_edit.setPlaceholderText("openai/gpt-3.5-turbo")
            self.api_endpoint_edit.setPlaceholderText("https://openrouter.ai/api/v1")
            
    def get_model_info(self) -> Dict[str, str]:
        """Возвращает информацию о модели."""
        return {
            "name": self.name_edit.text(),
            "provider": self.provider_combo.currentText(),
            "model_name": self.model_name_edit.text(),
            "access_token": self.api_key_edit.text(),
            "api_endpoint": self.api_endpoint_edit.text(),
            "streaming": self.stream_checkbox.isChecked()
        }

    def apply_theme(self):
        """Применяет текущую тему к окну и всем его элементам."""
        theme_mode = self.settings_manager.get_theme()
        style = get_style(theme_mode)
        self.setStyleSheet(style)
        self.update()

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
