"""Фабрика для создания провайдеров LLM."""
from .base_provider import BaseProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .openrouter_provider import OpenRouterProvider
from .google_provider import GoogleProvider
from .custom_provider import CustomProvider
from typing import Dict, Any, List
import asyncio

class LLMProviderFactory:
    """Фабрика провайдеров языковых моделей."""
    
    @staticmethod
    def get_provider(model_info: Dict[str, Any]) -> BaseProvider:
        """
        Создает и возвращает провайдера на основе информации о модели.
        
        Args:
            model_info: Словарь с информацией о модели
            
        Returns:
            BaseProvider: Экземпляр провайдера
        """
        provider_name = model_info.get('provider', '').lower()
        
        if provider_name == 'openai':
            return OpenAIProvider(model_info)
        elif provider_name == 'anthropic':
            return AnthropicProvider(model_info)
        elif provider_name == 'openrouter':
            return OpenRouterProvider(model_info)
        elif provider_name == 'google':
            return GoogleProvider(model_info)
        elif provider_name == 'custom':
            return CustomProvider(model_info)
        else:
            raise ValueError(f"Неизвестный провайдер: {provider_name}")

    @staticmethod
    async def get_all_available_models(api_keys: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Получает список всех доступных моделей от всех провайдеров.
        
        Args:
            api_keys: Словарь с API ключами для каждого провайдера
                     Пример: {"openai": "sk-...", "anthropic": "sk-...", ...}
        
        Returns:
            List[Dict[str, Any]]: Список всех доступных моделей
        """
        all_models = []
        
        # Создаем базовую конфигурацию для каждого провайдера
        providers_config = {
            "openai": {
                "provider": "openai",
                "api_endpoint": "https://api.openai.com/v1",
                "model_name": "gpt-3.5-turbo",
                "access_token": api_keys.get("openai", "")
            },
            "anthropic": {
                "provider": "anthropic",
                "api_endpoint": "https://api.anthropic.com",
                "model_name": "claude-2.1",
                "access_token": api_keys.get("anthropic", "")
            },
            "google": {
                "provider": "google",
                "api_endpoint": "",
                "model_name": "gemini-pro",
                "access_token": api_keys.get("google", "")
            },
            "openrouter": {
                "provider": "openrouter",
                "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "model_name": "openai/gpt-3.5-turbo",
                "access_token": api_keys.get("openrouter", "")
            },
            "custom": {
                "provider": "custom",
                "api_endpoint": "",
                "model_name": "",
                "access_token": api_keys.get("custom", "")
            }
        }
        
        # Создаем задачи для асинхронного получения моделей
        tasks = []
        for provider_name, config in providers_config.items():
            if config["access_token"] and provider_name != "custom":  # Получаем модели только если есть API ключ и провайдер не Custom
                provider = LLMProviderFactory.get_provider(config)
                tasks.append(provider.get_available_models())
        
        # Запускаем все задачи параллельно
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Обрабатываем результаты
            for result in results:
                if isinstance(result, list):  # Успешный результат
                    all_models.extend(result)
                else:  # Исключение
                    print(f"Error getting models: {result}")
        
        return sorted(all_models, key=lambda x: x["name"])
