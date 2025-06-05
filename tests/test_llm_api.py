import pytest
from unittest.mock import Mock, AsyncMock, patch
from llm_api import LLMApi
from settings_manager import SettingsManager


class TestLLMApi:
    def setup_method(self):
        """настройка для каждого теста"""
        self.mock_settings = Mock(spec=SettingsManager)
        self.mock_settings.get_prompt_info.return_value = {
            "name": "Базовый",
            "text": "Переведи текст"
        }
        
        self.model_info = {
            "name": "test_model",
            "provider": "OpenAI",
            "api_endpoint": "https://api.openai.com/v1",
            "model_name": "gpt-3.5-turbo",
            "access_token": "test_token"
        }

    def test_llm_api_initialization_valid(self):
        """тест успешной инициализации LLMApi"""
        with patch('llm_api.LLMProviderFactory.get_provider'):
            api = LLMApi(self.model_info, self.mock_settings)
            assert api.model_info == self.model_info
            assert api.settings_manager == self.mock_settings

    def test_llm_api_initialization_invalid_model_info(self):
        """тест инициализации с неверным model_info"""
        with pytest.raises(TypeError, match="model_info должен быть словарем"):
            LLMApi("invalid", self.mock_settings)

    def test_llm_api_initialization_invalid_settings(self):
        """тест инициализации с неверным settings_manager"""
        with pytest.raises(TypeError, match="settings_manager должен быть экземпляром SettingsManager"):
            LLMApi(self.model_info, "invalid")

    def test_update_system_prompt_with_prompt_info(self):
        """тест обновления системного промпта"""
        with patch('llm_api.LLMProviderFactory.get_provider'):
            api = LLMApi(self.model_info, self.mock_settings)
            api.update_system_prompt()
            assert api._system_prompt == "Переведи текст"

    def test_update_system_prompt_without_prompt_info(self):
        """тест обновления системного промпта без prompt_info"""
        self.mock_settings.get_prompt_info.return_value = None
        with patch('llm_api.LLMProviderFactory.get_provider'):
            api = LLMApi(self.model_info, self.mock_settings)
            api.update_system_prompt()
            assert "Переведи следующий текст" in api._system_prompt

    @pytest.mark.asyncio
    async def test_translate_success(self):
        """тест успешного перевода"""
        mock_provider = AsyncMock()
        mock_provider.translate.return_value = "Hello world"
        
        with patch('llm_api.LLMProviderFactory.get_provider', return_value=mock_provider):
            api = LLMApi(self.model_info, self.mock_settings)
            result = await api.translate("Привет мир", "English")
            
            assert result == "Hello world"
            mock_provider.translate.assert_called_once()

    @pytest.mark.asyncio
    async def test_translate_failure(self):
        """тест неудачного перевода"""
        mock_provider = AsyncMock()
        mock_provider.translate.side_effect = Exception("API Error")
        
        with patch('llm_api.LLMProviderFactory.get_provider', return_value=mock_provider):
            api = LLMApi(self.model_info, self.mock_settings)
            
            with pytest.raises(Exception, match="Ошибка перевода"):
                await api.translate("Привет мир", "English") 