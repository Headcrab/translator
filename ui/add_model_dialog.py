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
    QLabel,
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

    def __init__(self, parent=None, edit_model_data: Optional[Dict] = None):
        super().__init__(parent)
        self.settings_manager = SettingsManager()
        self.existing_models = {}  # Словарь для хранения существующих моделей
        self.all_models = []  # Список всех моделей для текущего провайдера
        self.provider_configs = LLMProviderFactory.get_provider_configs()

        self.setWindowTitle(
            "Редактировать модель" if edit_model_data else "Добавить модель"
        )

        layout = QVBoxLayout()

        # Поля ввода
        self.provider_combo = QComboBox()

        # Фильтруем провайдеров, у которых есть ключ API
        self.available_providers = {
            provider
            for provider, config in self.provider_configs.items()
            if os.getenv(config["env_var"])
        }

        # Если редактируем, добавляем провайдер текущей модели, даже если ключа нет
        if edit_model_data:
            self.available_providers.add(edit_model_data["provider"])

        if self.available_providers:
            self.provider_combo.addItems(sorted(list(self.available_providers)))
        else:
            self.provider_combo.addItem("Нет доступных провайдеров")
            self.provider_combo.setEnabled(False)

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
        form_layout.addRow("Провайдер:", self.provider_combo)
        form_layout.addRow("API Key Env:", self.api_key_edit)
        form_layout.addRow("Поиск:", self.search_edit)
        form_layout.addRow("Модель:", model_layout)
        form_layout.addRow(self.stream_checkbox)
        form_layout.addRow(self.progress_bar)

        layout.addLayout(form_layout)

        # Информационная метка, если нет провайдеров
        self.no_providers_label = QLabel(
            "Не найдены ключи API в переменных окружения.<br>"
            "Добавьте ключ (например, OPENAI_API_KEY) и перезапустите приложение."
        )
        self.no_providers_label.setAlignment(Qt.AlignCenter)
        self.no_providers_label.setWordWrap(True)
        self.no_providers_label.setVisible(not self.available_providers)
        layout.addWidget(self.no_providers_label)

        # Подсказки для разных провайдеров
        self.provider_combo.currentTextChanged.connect(self.on_provider_changed)

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal, self
        )
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

        if edit_model_data:
            self.provider_combo.setCurrentText(edit_model_data.get("provider", ""))
            provider_settings = self.settings_manager.get_provider_settings(
                edit_model_data.get("provider", "")
            )
            self.api_key_edit.setText(provider_settings.get("access_token_env", ""))
            self.model_name_edit.setEditText(edit_model_data.get("model_name", ""))
            self.stream_checkbox.setChecked(edit_model_data.get("streaming", False))

        # Блокируем поля, если нет провайдеров
        if not self.available_providers:
            for w in [
                self.search_edit,
                self.model_name_edit,
                self.refresh_models_button,
                self.stream_checkbox,
                self.api_key_edit,
            ]:
                w.setEnabled(False)

    def filter_models(self, search_text: str):
        """Фильтрует список моделей на основе поискового запроса."""
        provider = self.provider_combo.currentText()

        # Сохраняем текущий выбор
        current_text = self.model_name_edit.currentText()

        # Очищаем список
        self.model_name_edit.clear()

        # Фильтруем и добавляем только новые модели
        for model in self.all_models:
            if search_text.lower() in model[
                "model_name"
            ].lower() and not self.is_model_exists(model["model_name"], provider):
                self.model_name_edit.addItem(
                    self.style().standardIcon(self.style().SP_FileIcon),
                    model["model_name"],
                    model,
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

    def on_provider_changed(self, provider: str):
        """Обновляет подсказки в зависимости от выбранного провайдера."""
        if not self.available_providers:
            return

        # Очищаем список моделей и сбрасываем поиск
        self.model_name_edit.clear()
        self.search_edit.clear()
        self.all_models.clear()

        # Устанавливаем значения по умолчанию для каждого провайдера
        provider_settings = self.settings_manager.get_provider_settings(provider)
        self.api_key_edit.setText(
            provider_settings.get("access_token_env")
            or self.provider_configs.get(provider, {}).get("env_var", "")
        )

        # Обновляем список доступных моделей для нового провайдера
        self.fetch_available_models()

    async def _fetch_models(self):
        """Асинхронно получает список моделей от выбранного провайдера."""
        provider = self.provider_combo.currentText()
        api_key_env = self.api_key_edit.text().strip()
        api_key = os.getenv(api_key_env, "")

        if not api_key:
            QMessageBox.warning(
                self,
                "Ошибка",
                f"API ключ не найден. Пожалуйста, установите переменную окружения {api_key_env}",
            )
            return []

        provider_settings = self.settings_manager.get_provider_settings(provider)
        endpoint = provider_settings.get("api_endpoint")

        self.settings_manager.set_provider_settings(provider, api_key_env, endpoint)

        config = {
            "provider": provider.lower(),
            "api_endpoint": endpoint,
            "model_name": "",  # Не используется для получения списка
            "access_token": api_key,
        }

        try:
            # Создаем провайдер через фабрику
            provider_instance = LLMProviderFactory.get_provider(config)
            models = await provider_instance.get_available_models()
            return models
        except Exception as e:
            QMessageBox.warning(
                self, "Ошибка", f"Не удалось получить список моделей: {str(e)}"
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
                    model
                    for model in self.existing_models.values()
                    if model["provider"] == provider
                ]
                for model in existing_provider_models:
                    self.model_name_edit.addItem(
                        self.style().standardIcon(self.style().SP_DialogApplyButton),
                        model["model_name"],
                        model,
                    )

                # Добавляем новые модели
                for model in models:
                    # Проверяем, не существует ли уже такая модель
                    if not self.is_model_exists(model["model_name"], provider):
                        display_name = model["model_name"]
                        self.model_name_edit.addItem(
                            self.style().standardIcon(self.style().SP_FileIcon),
                            display_name,
                            model,
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
                    self, "Ошибка", f"Не удалось получить список моделей: {str(e)}"
                )
            finally:
                self.refresh_models_button.setEnabled(True)
                self.progress_bar.hide()

        # Запускаем асинхронную операцию
        asyncio.create_task(fetch())

    def get_model_info(self) -> Optional[Dict[str, str]]:
        """Собирает информацию о модели из диалогового окна."""
        provider = self.provider_combo.currentText()
        access_token_env = self.api_key_edit.text().strip()

        provider_settings = self.settings_manager.get_provider_settings(provider)
        self.settings_manager.set_provider_settings(
            provider, access_token_env, provider_settings.get("api_endpoint")
        )

        if not os.getenv(access_token_env):
            QMessageBox.warning(
                self,
                "Внимание",
                f"Переменная окружения '{access_token_env}' не установлена. Модель может не работать.",
            )

        model_name = self.model_name_edit.currentText().strip()

        if not all([provider, model_name]):
            QMessageBox.warning(
                self, "Ошибка", "Пожалуйста, выберите провайдера и модель."
            )
            return None

        return {
            "provider": provider,
            "model_name": model_name,
            "streaming": self.stream_checkbox.isChecked(),
        }

    def apply_theme(self):
        """Применяет текущую тему к диалогу."""
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
