"""Диалог добавления новой модели."""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QFormLayout,
    QDialogButtonBox,
    QPushButton,
    QMessageBox,
    QProgressBar,
    QLabel
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from settings_manager import SettingsManager
from .styles import get_style
from typing import Dict, Optional
from providers.llm_provider_factory import LLMProviderFactory
import asyncio
import os
# убрать предупреждение линтера
import ui.resources_rc  # noqa: F401  # Импорт скомпилированных ресурсов


class AddModelDialog(QDialog):
    """Диалоговое окно для добавления новой модели."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings_manager = SettingsManager()
        self.existing_models = {}  # Словарь для хранения существующих моделей
        self.all_models = []  # Список всех моделей для текущего провайдера
        
        self.setWindowTitle("Добавить модель")
        
        layout = QVBoxLayout()
        
        # Поля ввода
        self.name_edit = QLineEdit()
        self.provider_combo = QComboBox()
        self.provider_combo.addItems([
            "OpenAI",
            "Anthropic", 
            "Google",
            "OpenRouter",
            "Custom"
        ])
        
        # Поле поиска моделей
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск модели...")
        self.search_edit.textChanged.connect(self.filter_models)
        
        self.model_name_edit = QComboBox()
        self.model_name_edit.setEditable(True)
        self.model_name_edit.setInsertPolicy(QComboBox.InsertPolicy.InsertAtBottom)
        
        # Создаем горизонтальный layout для модели и кнопки
        model_layout = QHBoxLayout()
        model_layout.addWidget(self.model_name_edit)
        
        # Кнопка для получения списка моделей
        self.refresh_models_button = QPushButton()
        self.refresh_models_button.setObjectName("refresh_models_button")
        self.refresh_models_button.setIcon(QIcon(":/icons/refresh.svg"))
        self.refresh_models_button.setFixedSize(24, 24)
        self.refresh_models_button.setIconSize(QSize(16, 16))
        self.refresh_models_button.setToolTip("Получить список моделей")
        self.refresh_models_button.clicked.connect(self.fetch_available_models)
        model_layout.addWidget(self.refresh_models_button)
        
        self.api_endpoint_edit = QLineEdit()
        self.stream_checkbox = QCheckBox("Использовать потоковый режим")
        
        # Добавляем поле для API ключа
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Имя переменной окружения для API ключа")
        
        # Прогресс бар для индикации загрузки
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Бесконечная анимация
        self.progress_bar.hide()
        
        # Добавляем поля в layout
        form_layout = QFormLayout()
        form_layout.addRow("Название:", self.name_edit)
        form_layout.addRow("Провайдер:", self.provider_combo)
        form_layout.addRow("API Key:", self.api_key_edit)
        form_layout.addRow("Поиск:", self.search_edit)
        form_layout.addRow("Модель:", model_layout)
        self.api_endpoint_label = QLabel("API endpoint:")
        form_layout.addRow(self.api_endpoint_label, self.api_endpoint_edit)
        form_layout.addRow(self.stream_checkbox)
        form_layout.addRow(self.progress_bar)
        
        layout.addLayout(form_layout)
        
        # Подсказки для разных провайдеров и автоматическое формирование названия
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)
        self.model_name_edit.currentTextChanged.connect(self.update_model_name)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Загружаем существующие модели
        self.load_existing_models()
        
        # Инициализация начальных значений
        self.on_provider_changed(self.provider_combo.currentText())
        self.adjustSize()
        self.resize(self.width() + 100, self.height())
        
    def filter_models(self, search_text: str):
        """Фильтрует список моделей на основе поискового запроса."""
        provider = self.provider_combo.currentText()
        
        # Сохраняем текущий выбор
        current_text = self.model_name_edit.currentText()
        
        # Очищаем список
        self.model_name_edit.clear()
        
        # Фильтруем и добавляем только новые модели
        for model in self.all_models:
            if (search_text.lower() in model["model_name"].lower() and
                not self.is_model_exists(model["model_name"], provider)):
                self.model_name_edit.addItem(
                    self.style().standardIcon(self.style().SP_FileIcon),
                    model["model_name"],
                    model
                )
        
        # Восстанавливаем выбор, если возможно
        if current_text:
            index = self.model_name_edit.findText(current_text)
            if index >= 0:
                self.model_name_edit.setCurrentIndex(index)
                
    def load_existing_models(self):
        """Загружает список существующих моделей."""
        models, _ = self.settings_manager.get_models()
        for model in models:
            key = f"{model['model_name']} - {model['provider']}"
            self.existing_models[key] = model
            
    def is_model_exists(self, model_name: str, provider: str) -> Optional[Dict]:
        """Проверяет, существует ли модель с таким именем и провайдером."""
        key = f"{model_name} - {provider}"
        return self.existing_models.get(key)
        
    def update_model_name(self, model_name: str):
        """Обновляет название модели на основе выбранного провайдера и имени модели в формате 'model_identifier - Provider'."""
        if not model_name:
            return
            
        provider = self.provider_combo.currentText()
        model_data = self.model_name_edit.currentData()
        
        if model_data and isinstance(model_data, dict):
            identifier = model_data.get("model_name", model_name)
        else:
            identifier = model_name.split(" - ")[0] if " - " in model_name else model_name
            
        # Проверяем, существует ли такая модель
        existing_model = self.is_model_exists(identifier, provider)
        if existing_model:
            # Если модель существует, заполняем поля её данными, но не меняем название
            self.api_endpoint_edit.setText(existing_model["api_endpoint"])
            self.stream_checkbox.setChecked(existing_model.get("streaming", False))
            if existing_model.get("access_token"):
                self.api_key_edit.setText(existing_model["access_token"])
        else:
            # Если модель новая, генерируем новое имя
            new_name = f"{identifier} - {provider}"
            self.name_edit.setText(new_name)
        
    def on_provider_changed(self, provider: str):
        """Обновляет подсказки в зависимости от выбранного провайдера."""
        # Очищаем список моделей и сбрасываем поиск
        self.model_name_edit.clear()
        self.search_edit.clear()
        self.all_models.clear()
        
        # Скрываем/показываем поле endpoint в зависимости от провайдера
        is_google = provider == "Google"
        self.api_endpoint_edit.setVisible(not is_google)
        self.api_endpoint_label.setVisible(not is_google)
        
        # Устанавливаем значения по умолчанию для каждого провайдера
        provider_defaults = {
            "OpenAI": {
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "env_var": "OPENAI_API_KEY"
            },
            "Anthropic": {
                "endpoint": "https://api.anthropic.com/v1/messages",
                "env_var": "ANTHROPIC_API_KEY"
            },
            "Google": {
                "endpoint": "",
                "env_var": "GOOGLE_API_KEY"
            },
            "OpenRouter": {
                "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "env_var": "OPENROUTER_API_KEY"
            },
            "Custom": {
                "endpoint": "",
                "env_var": "CUSTOM_API_KEY"
            }
        }
        
        defaults = provider_defaults.get(provider, {"endpoint": "", "env_var": ""})
        self.api_endpoint_edit.setText(defaults["endpoint"])
        self.api_key_edit.setText(defaults["env_var"])
        
        # Обновляем список доступных моделей для нового провайдера
        self.fetch_available_models()
        
        # Обновляем название при смене провайдера
        self.update_model_name(self.model_name_edit.currentText())
        
    async def _fetch_models(self):
        """Асинхронно получает список моделей от выбранного провайдера."""
        provider = self.provider_combo.currentText()
        api_key_env = self.api_key_edit.text().strip()
        api_key = os.getenv(api_key_env, "")
        
        if not api_key:
            QMessageBox.warning(
                self,
                "Ошибка",
                f"API ключ не найден. Пожалуйста, установите переменную окружения {api_key_env}"
            )
            return []
            
        # Получаем endpoint в зависимости от провайдера
        endpoint = self.api_endpoint_edit.text().strip()
        if provider == "Custom":
            if not endpoint:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    "Для Custom провайдера необходимо указать API endpoint"
                )
                return []
            # Добавляем /chat/completions к URL если его нет
            if not endpoint.endswith("/chat/completions"):
                endpoint = endpoint.rstrip("/") + "/chat/completions"
        
        # Создаем конфигурацию для провайдера
        provider_config = {
            "provider": provider,
            "api_endpoint": endpoint,
            "model_name": "gpt-3.5-turbo",  # Временное значение для инициализации
            "access_token": api_key_env,
        }
        
        try:
            # Создаем провайдер через фабрику
            provider_instance = LLMProviderFactory.get_provider(provider_config)
            models = await provider_instance.get_available_models()
            return models
        except Exception as e:
            QMessageBox.warning(
                self,
                "Ошибка",
                f"Не удалось получить список моделей: {str(e)}"
            )
            return []
        
    def fetch_available_models(self):
        """Получает список доступных моделей от провайдера."""
        self.refresh_models_button.setEnabled(False)
        self.progress_bar.show()
        
        async def fetch():
            try:
                models = await self._fetch_models()
                provider = self.provider_combo.currentText()
                
                # Сохраняем текущий выбор
                current_text = self.model_name_edit.currentText()
                
                # Очищаем список и сохраняем все модели
                self.model_name_edit.clear()
                self.all_models = models
                
                # Добавляем существующие модели
                existing_provider_models = [
                    model for model in self.existing_models.values()
                    if model["provider"] == provider
                ]
                for model in existing_provider_models:
                    self.model_name_edit.addItem(
                        self.style().standardIcon(self.style().SP_DialogApplyButton),
                        model["model_name"],
                        model
                    )
                
                # Добавляем новые модели
                for model in models:
                    # Проверяем, не существует ли уже такая модель
                    if not self.is_model_exists(model["model_name"], provider):
                        display_name = model["model_name"]
                        self.model_name_edit.addItem(
                            self.style().standardIcon(self.style().SP_FileIcon),
                            display_name,
                            model
                        )
                
                # Восстанавливаем выбор, если возможно
                if current_text:
                    index = self.model_name_edit.findText(current_text)
                    if index >= 0:
                        self.model_name_edit.setCurrentIndex(index)
                        
                # Применяем текущий фильтр поиска
                self.filter_models(self.search_edit.text())
                    
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Ошибка",
                    f"Не удалось получить список моделей: {str(e)}"
                )
            finally:
                self.refresh_models_button.setEnabled(True)
                self.progress_bar.hide()
        
        # Запускаем асинхронную операцию
        asyncio.create_task(fetch())
        
    def get_model_info(self) -> Optional[Dict[str, str]]:
        """Возвращает информацию о модели."""
        name = self.name_edit.text().strip()
        provider = self.provider_combo.currentText()
        api_endpoint = self.api_endpoint_edit.text().strip()
        api_key_env = self.api_key_edit.text().strip()
        
        # Получаем имя модели
        if provider == "Custom":
            # Для Custom провайдера берем значение напрямую из поля ввода
            model_name = self.model_name_edit.currentText().strip()
        else:
            # Для остальных провайдеров используем логику с currentData
            model_name = self.model_name_edit.currentText()
            current_data = self.model_name_edit.currentData()
            if current_data and isinstance(current_data, dict):
                model_name = current_data["model_name"]
        
        # Проверяем обязательные поля
        required_fields = [name, provider, model_name, api_key_env]
        if provider != "Google":
            required_fields.append(api_endpoint)
            
        if not all(required_fields):
            QMessageBox.warning(
                self,
                "Ошибка",
                "Пожалуйста, заполните все обязательные поля"
            )
            return None
            
        # Создаем базовую конфигурацию модели
        model_info = {
            "name": name,
            "provider": provider,
            "model_name": model_name,
            "api_endpoint": api_endpoint if provider != "Google" else "",
            "access_token_env": api_key_env,
            "streaming": self.stream_checkbox.isChecked()
        }
        
        return model_info

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
