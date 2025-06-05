import pytest
from unittest.mock import Mock, patch, AsyncMock
from settings_manager import SettingsManager
from llm_api import LLMApi


class TestIntegration:
    """интеграционные тесты для основного потока приложения"""
    
    def setup_method(self):
        """настройка для интеграционных тестов"""
        SettingsManager._instance = None  # сброс singleton
    
    def teardown_method(self):
        """очистка после тестов"""
        SettingsManager._instance = None

    def test_settings_to_llm_api_integration(self):
        """тест интеграции SettingsManager с LLMApi"""
        # Создаем настройки
        settings = SettingsManager()
        
        # Настраиваем модель
        model_info = {
            "name": "test_model",
            "provider": "OpenAI",
            "api_endpoint": "https://api.openai.com/v1",
            "model_name": "gpt-3.5-turbo",
            "access_token": "test_token"
        }
        
        # Тестируем создание LLMApi с реальными настройками
        with patch('llm_api.LLMProviderFactory.get_provider'):
            api = LLMApi(model_info, settings)
            assert api.settings_manager == settings
            assert api.model_info == model_info

    @pytest.mark.asyncio
    async def test_full_translation_flow(self):
        """тест полного потока перевода"""
        # Создаем компоненты
        settings = SettingsManager()
        
        model_info = {
            "name": "test_model",
            "provider": "OpenAI",
            "api_endpoint": "https://api.openai.com/v1",
            "model_name": "gpt-3.5-turbo",
            "access_token": "test_token"
        }
        
        # Мокаем провайдер
        mock_provider = AsyncMock()
        mock_provider.translate.return_value = "Hello world"
        
        with patch('llm_api.LLMProviderFactory.get_provider', return_value=mock_provider):
            # Создаем LLMApi
            api = LLMApi(model_info, settings)
            
            # Выполняем перевод
            result = await api.translate("Привет мир", "English")
            
            # Проверяем результат
            assert result == "Hello world"
            
            # Проверяем что провайдер был вызван с правильными параметрами
            mock_provider.translate.assert_called_once()
            call_args = mock_provider.translate.call_args[0]
            messages = call_args[0]
            target_lang = call_args[1]
            
            assert target_lang == "English"
            assert len(messages) == 2  # system и user messages
            assert messages[0]["role"] == "system"
            assert messages[1]["role"] == "user"
            assert messages[1]["content"] == "Привет мир"

    def test_hotkey_settings_integration(self):
        """тест интеграции настроек горячих клавиш"""
        settings = SettingsManager()
        
        # Устанавливаем горячую клавишу
        settings.set_hotkey(["ctrl", "shift"], "T")
        
        # Получаем горячую клавишу
        modifiers, key = settings.get_hotkey()
        
        assert modifiers == ["ctrl", "shift"]
        assert key == "T"
        
        # Формируем строку для keyboard модуля
        hotkey_string = "+".join(modifiers) + "+" + key
        assert hotkey_string == "ctrl+shift+T"

    def test_model_management_flow(self):
        """тест потока управления моделями"""
        settings = SettingsManager()
        
        # Добавляем модель
        settings.add_model(
            name="test_model",
            provider="OpenAI",
            api_endpoint="https://api.openai.com/v1",
            model_name="gpt-3.5-turbo",
            access_token="test_token"
        )
        
        # Устанавливаем как текущую
        settings.set_current_model("test_model")
        
        # Получаем информацию о модели
        model_info = settings.get_model_info("test_model")
        
        assert model_info is not None
        assert model_info["name"] == "test_model"
        assert model_info["provider"] == "OpenAI"
        
        # Проверяем список моделей
        models, current_model = settings.get_models()
        assert len(models) > 0
        assert current_model["name"] == "test_model" 