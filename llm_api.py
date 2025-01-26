"""Модуль для работы с API различных LLM моделей."""

from typing import Dict, Any
from settings_manager import SettingsManager
from providers.llm_provider_factory import LLMProviderFactory

class LLMApi:
    """Класс для работы с API различных LLM моделей."""
    
    def __init__(self, model_info: Dict[str, Any], settings_manager: SettingsManager):
        """
        Инициализация клиента API.
        
        Args:
            model_info: Словарь с информацией о модели:
                - name: Имя модели
                - provider: Провайдер (OpenAI, Anthropic, Google, OpenRouter)
                - api_endpoint: URL эндпоинта API
                - model_name: Название модели у провайдера
                - access_token: Токен доступа к API
        """
        if not isinstance(model_info, dict):
            raise TypeError("model_info должен быть словарем")
            
        if not isinstance(settings_manager, SettingsManager):
            raise TypeError("settings_manager должен быть экземпляром SettingsManager")
            
        self.model_info = model_info
        self.settings_manager = settings_manager
        self.provider = LLMProviderFactory.get_provider(model_info)
        
    async def translate(self, text: str, target_lang: str, streaming_callback=None) -> str:
        """Выполняет перевод с поддержкой потокового режима."""
        if not text:
            return ""
            
        system_prompt = self.settings_manager.get_system_prompt()
        
        messages = [
            {"role": "system", "content": system_prompt.format(language=target_lang)},
            {"role": "user", "content": text}
        ]
        
        if not self.provider:
            raise RuntimeError("Провайдер не инициализирован")
            
        try:
            result = await self.provider.translate(messages, target_lang, streaming_callback)
            return result if result else ""
        except Exception as e:
            print(f"Ошибка перевода: {e}")
            return "Ошибка перевода"

