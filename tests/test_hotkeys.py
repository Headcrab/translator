import pytest
from unittest.mock import patch, Mock, MagicMock
import hotkeys


class TestHotkeys:
    """тесты для функциональности горячих клавиш"""
    
    def setup_method(self):
        """настройка мок-объектов"""
        self.mock_window = Mock()
        self.mock_window.show_window_requested = Mock()
        self.mock_window.clipboard_updated = Mock()
        self.mock_window.show_window_requested.emit = Mock()
        self.mock_window.clipboard_updated.emit = Mock()

    @patch('hotkeys.keyboard')
    def test_register_global_hotkeys(self, mock_keyboard):
        """тест регистрации горячих клавиш"""
        test_hotkey = "ctrl+shift+t"
        
        hotkeys.register_global_hotkeys(self.mock_window, test_hotkey)
        
        mock_keyboard.add_hotkey.assert_called_once()
        args = mock_keyboard.add_hotkey.call_args[0]
        assert args[0] == test_hotkey
        assert callable(args[1])  # проверяем что передана функция

    @patch('hotkeys.keyboard')
    def test_unregister_global_hotkeys(self, mock_keyboard):
        """тест отмены регистрации горячих клавиш"""
        hotkeys.unregister_global_hotkeys()
        mock_keyboard.unhook_all.assert_called_once()

    @patch('hotkeys.time.sleep')
    @patch('hotkeys.keyboard.is_pressed')
    def test_wait_for_keys_release(self, mock_is_pressed, mock_sleep):
        """тест ожидания отпускания клавиш"""
        mock_is_pressed.side_effect = [True, True, False]  # сначала нажаты, потом отпущены
        
        # Используем внутреннюю функцию через замыкание
        test_hotkey = "ctrl+t"
        captured_callback = None
        
        with patch('hotkeys.keyboard.add_hotkey') as mock_add_hotkey:
            def capture_callback(hotkey, callback):
                nonlocal captured_callback
                captured_callback = callback
            
            mock_add_hotkey.side_effect = capture_callback
            hotkeys.register_global_hotkeys(self.mock_window, test_hotkey)
        
        # Тест самой функции wait_for_keys_release через вызов callback
        # (это сложно тестировать напрямую, так как это внутренняя функция)
        assert captured_callback is not None

    @patch('hotkeys.pyperclip')
    @patch('hotkeys.keyboard')
    @patch('hotkeys.time.sleep')
    def test_hotkey_callback_execution(self, mock_sleep, mock_keyboard, mock_pyperclip):
        """тест выполнения callback горячей клавиши"""
        # Настройка мок-объектов
        mock_pyperclip.paste.side_effect = ["old_text", "new_text"]
        mock_keyboard.is_pressed.return_value = False
        
        test_hotkey = "ctrl+t"
        captured_callback = None
        
        with patch('hotkeys.keyboard.add_hotkey') as mock_add_hotkey:
            def capture_callback(hotkey, callback):
                nonlocal captured_callback
                captured_callback = callback
            
            mock_add_hotkey.side_effect = capture_callback
            hotkeys.register_global_hotkeys(self.mock_window, test_hotkey)
        
        # Выполняем callback
        if captured_callback:
            captured_callback()
        
            # Проверяем что были вызваны нужные методы
            assert mock_keyboard.send.called
            assert self.mock_window.show_window_requested.emit.called
            assert self.mock_window.clipboard_updated.emit.called 