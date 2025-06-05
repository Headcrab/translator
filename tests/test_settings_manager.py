import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from settings_manager import SettingsManager


class TestSettingsManager:
    def setup_method(self):
        """создание временной директории для тестов"""
        self.test_dir = tempfile.mkdtemp()
        self.test_config_path = os.path.join(self.test_dir, "test_settings.json")
        
    def teardown_method(self):
        """очистка временной директории"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        # очистка singleton
        SettingsManager._instance = None
    
    def test_settings_manager_initialization(self):
        """тест инициализации SettingsManager"""
        with patch.object(SettingsManager, '__init__', lambda x: None):
            manager = SettingsManager()
            assert manager is not None
            
    def test_get_hotkey_default(self):
        """тест получения hotkey по умолчанию"""
        manager = SettingsManager()
        modifiers, key = manager.get_hotkey()
        assert isinstance(modifiers, list)
        assert isinstance(key, str)
        assert len(modifiers) > 0
        assert len(key) > 0
            
    def test_get_models(self):
        """тест получения списка моделей"""
        manager = SettingsManager()
        models, current_model = manager.get_models()
        assert isinstance(models, list) 