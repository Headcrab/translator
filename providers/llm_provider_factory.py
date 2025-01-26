"""Фабрика для создания провайдеров LLM."""
from .base_provider import BaseProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .openrouter_provider import OpenRouterProvider
from .google_provider import GoogleProvider
from typing import Dict, Any

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
        else:
            raise ValueError(f"Неизвестный провайдер: {provider_name}")
