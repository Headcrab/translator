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

    @staticmethod
    def get_provider_by_name(provider_name: str) -> BaseProvider:
        """Создает экземпляр провайдера на основе имени провайдера."""
        if not provider_name:
            raise ValueError("Не указан провайдер")
            
        provider_map = {
            "OpenAI": OpenAIProvider,
            "Anthropic": AnthropicProvider,
            "OpenRouter": OpenRouterProvider,
            "Google": GoogleProvider
        }
        
        provider_class = provider_map.get(provider_name)
        if not provider_class:
            raise ValueError(f"Неподдерживаемый провайдер: {provider_name}")
            
        # Добавляем проверку обязательных полей для OpenRouter
        if provider_name == "OpenRouter":
            required_fields = [
                "model_name", 
                "access_token"
            ]
            for field in required_fields:
                if field not in model_info:
                    raise ValueError(f"Отсутствует поле {field} для OpenRouter")
            
            if not model_info.get("stream_options"):
                model_info["stream_options"] = {"include_usage": True}
        
        return provider_class(model_info) 