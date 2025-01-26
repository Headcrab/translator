"""Фабрика для создания провайдеров LLM."""
from .base_provider import BaseProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .openrouter_provider import OpenRouterProvider

class LLMProviderFactory:
    """Фабрика провайдеров языковых моделей."""
    
    @staticmethod
    def get_provider(model_info: dict) -> BaseProvider:
        """Создает экземпляр провайдера на основе конфигурации."""
        if not model_info:
            raise ValueError("Отсутствует конфигурация модели")
            
        provider_map = {
            "OpenAI": OpenAIProvider,
            "Anthropic": AnthropicProvider,
            "OpenRouter": OpenRouterProvider
        }
        
        provider_name = model_info.get("provider")
        if not provider_name:
            raise ValueError("Не указан провайдер в конфигурации модели")
        
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