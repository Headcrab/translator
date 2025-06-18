"""Фабрика для создания провайдеров LLM."""

from .base_provider import BaseProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .openrouter_provider import OpenRouterProvider
from .google_provider import GoogleProvider
from .custom_provider import CustomProvider
from typing import Dict, Any, List
import asyncio
import logging

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Фабрика провайдеров языковых моделей."""

    @staticmethod
    def get_provider_configs() -> Dict[str, Dict[str, str]]:
        """Возвращает конфигурации для всех провайдеров."""
        return {
            "OpenAI": {
                "endpoint": "https://api.openai.com/v1/chat/completions",
                "env_var": "OPENAI_API_KEY",
            },
            "Anthropic": {
                "endpoint": "https://api.anthropic.com/v1/messages",
                "env_var": "ANTHROPIC_API_KEY",
            },
            "Google": {"endpoint": "", "env_var": "GOOGLE_API_KEY"},
            "OpenRouter": {
                "endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "env_var": "OPENROUTER_API_KEY",
            },
            "Cerebras": {
                "endpoint": "https://api.cerebras.ai/v1",
                "env_var": "CEREBRAS_API_KEY",
            },
            "Nebius": {
                "endpoint": "https://api.studio.nebius.ai/v1/",
                "env_var": "NEBIUS_API_KEY",
            },
        }

    @staticmethod
    def get_provider(model_info: Dict[str, Any]) -> BaseProvider:
        """
        Создает и возвращает провайдера на основе информации о модели.

        Args:
            model_info: Словарь с информацией о модели

        Returns:
            BaseProvider: Экземпляр провайдера
        """
        provider_name = model_info.get("provider", "").lower()

        if provider_name == "openai":
            return OpenAIProvider(model_info)
        elif provider_name == "anthropic":
            return AnthropicProvider(model_info)
        elif provider_name == "openrouter":
            return OpenRouterProvider(model_info)
        elif provider_name == "google":
            return GoogleProvider(model_info)
        elif provider_name in ["custom", "cerebras", "nebius"]:
            return CustomProvider(model_info)
        else:
            raise ValueError(f"Неизвестный провайдер: {provider_name}")

    @staticmethod
    async def get_all_available_models(
        api_keys: Dict[str, str],
    ) -> List[Dict[str, Any]]:
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
                "access_token": api_keys.get("openai", ""),
            },
            "anthropic": {
                "provider": "anthropic",
                "api_endpoint": "https://api.anthropic.com",
                "model_name": "claude-2.1",
                "access_token": api_keys.get("anthropic", ""),
            },
            "google": {
                "provider": "google",
                "api_endpoint": "",
                "model_name": "gemini-pro",
                "access_token": api_keys.get("google", ""),
            },
            "openrouter": {
                "provider": "openrouter",
                "api_endpoint": "https://openrouter.ai/api/v1/chat/completions",
                "model_name": "openai/gpt-3.5-turbo",
                "access_token": api_keys.get("openrouter", ""),
            },
        }

        # Создаем задачи для асинхронного получения моделей
        tasks = []
        for provider_name, config in providers_config.items():
            if config["access_token"]:  # Получаем модели только если есть API ключ
                provider = LLMProviderFactory.get_provider(config)
                tasks.append(provider.get_available_models())

        # Запускаем все задачи параллельно
        if tasks:
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Обрабатываем результаты
                for result in results:
                    if isinstance(result, list):  # Успешный результат
                        all_models.extend(result)
                    else:  # Исключение
                        logger.error(
                            f"Ошибка при получении списка моделей: {str(result)}"
                        )

            except Exception as e:
                logger.error(f"Ошибка при получении списка моделей: {str(e)}")
                return []

        return sorted(all_models, key=lambda x: x["name"])
