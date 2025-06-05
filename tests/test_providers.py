import pytest
from unittest.mock import Mock, patch, AsyncMock
from providers.llm_provider_factory import LLMProviderFactory
from providers.base_provider import BaseProvider


class TestLLMProviderFactory:
    def test_get_provider_openai(self):
        """тест получения OpenAI провайдера"""
        model_info = {
            "provider": "OpenAI",
            "api_endpoint": "https://api.openai.com/v1",
            "model_name": "gpt-3.5-turbo",
            "access_token": "test_token"
        }
        
        with patch('providers.llm_provider_factory.OpenAIProvider') as mock_provider:
            provider = LLMProviderFactory.get_provider(model_info)
            # провайдеры принимают model_info целиком
            mock_provider.assert_called_once_with(model_info)

    def test_get_provider_anthropic(self):
        """тест получения Anthropic провайдера"""
        model_info = {
            "provider": "Anthropic",
            "api_endpoint": "https://api.anthropic.com/v1",
            "model_name": "claude-3",
            "access_token": "test_token"
        }
        
        with patch('providers.llm_provider_factory.AnthropicProvider') as mock_provider:
            provider = LLMProviderFactory.get_provider(model_info)
            mock_provider.assert_called_once()

    def test_get_provider_invalid(self):
        """тест получения несуществующего провайдера"""
        model_info = {
            "provider": "InvalidProvider",
            "api_endpoint": "https://test.com",
            "model_name": "test",
            "access_token": "test_token"
        }
        
        with pytest.raises(ValueError, match="Неизвестный провайдер"):
            LLMProviderFactory.get_provider(model_info)


class TestBaseProvider:
    def test_base_provider_initialization(self):
        """тест инициализации базового провайдера"""
        # BaseProvider абстрактный, создаем mock подкласс
        class MockProvider(BaseProvider):
            async def translate(self, messages, target_lang, streaming_callback=None):
                return "mock translation"
            
            async def get_available_models(self):
                return []
        
        model_info = {
            "api_endpoint": "https://api.test.com",
            "model_name": "test-model",
            "access_token": "test-token"
        }
        
        provider = MockProvider(model_info)
        assert provider.api_endpoint == "https://api.test.com"
        assert provider.model_name == "test-model"
        assert provider.access_token == "test-token"

    @pytest.mark.asyncio
    async def test_base_provider_abstract_methods(self):
        """тест что абстрактные методы должны быть реализованы"""
        # Проверяем что BaseProvider нельзя инстанциировать
        model_info = {
            "api_endpoint": "https://api.test.com",
            "model_name": "test-model",
            "access_token": "test-token"
        }
        
        with pytest.raises(TypeError):
            BaseProvider(model_info) 