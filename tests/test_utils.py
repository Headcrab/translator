import pytest
import os
import tempfile
from unittest.mock import patch, Mock
import pyperclip


class TestClipboardOperations:
    """тесты для операций с буфером обмена"""
    
    def test_clipboard_copy_paste(self):
        """тест копирования и вставки из буфера обмена"""
        test_text = "Test clipboard text"
        pyperclip.copy(test_text)
        result = pyperclip.paste()
        assert result == test_text

    def test_clipboard_empty(self):
        """тест пустого буфера обмена"""
        pyperclip.copy("")
        result = pyperclip.paste()
        assert result == ""

    def test_clipboard_unicode(self):
        """тест unicode текста в буфере обмена"""
        test_text = "Привет мир! 🌍"
        pyperclip.copy(test_text)
        result = pyperclip.paste()
        assert result == test_text


class TestFileOperations:
    """тесты для файловых операций"""
    
    def setup_method(self):
        """создание временного файла для тестов"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.json")
    
    def teardown_method(self):
        """очистка временных файлов"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        os.rmdir(self.temp_dir)
    
    def test_file_exists_check(self):
        """тест проверки существования файла"""
        assert not os.path.exists(self.test_file)
        
        with open(self.test_file, 'w') as f:
            f.write('{"test": true}')
        
        assert os.path.exists(self.test_file)

    def test_file_read_write(self):
        """тест чтения и записи файла"""
        test_content = "Test file content"
        
        with open(self.test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        with open(self.test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert content == test_content 