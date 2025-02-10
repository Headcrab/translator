"""Диалог для добавления/редактирования системных промптов."""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QMessageBox,
)
# from PyQt5.QtCore import Qt
from .styles import get_style


class AddPromptDialog(QDialog):
    """Диалог для добавления/редактирования системных промптов."""

    def __init__(self, parent=None, prompt_info=None):
        """
        Инициализация диалога.
        
        Args:
            parent: Родительское окно
            prompt_info: Информация о промпте для редактирования (если None - создание нового)
        """
        super().__init__(parent)
        self.prompt_info = prompt_info
        self.setWindowTitle("Добавить промпт" if not prompt_info else "Редактировать промпт")
        self.setModal(True)
        self.setup_ui()
        
        if prompt_info:
            self.load_prompt_info()

    def setup_ui(self):
        """Настройка интерфейса."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Название промпта
        name_layout = QVBoxLayout()
        name_label = QLabel("Название:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введите название промпта")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        # Текст промпта
        text_layout = QVBoxLayout()
        text_label = QLabel("Текст промпта:")
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Введите текст промпта")
        self.text_edit.setMinimumHeight(200)
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.text_edit)
        layout.addLayout(text_layout)

        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)

        buttons_layout.addWidget(self.ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

        # Устанавливаем размеры окна
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

    def load_prompt_info(self):
        """Загружает информацию о промпте в поля формы."""
        if self.prompt_info:
            self.name_edit.setText(self.prompt_info["name"])
            self.text_edit.setPlainText(self.prompt_info["text"])

    def get_prompt_info(self):
        """Возвращает информацию о промпте из полей формы."""
        name = self.name_edit.text().strip()
        text = self.text_edit.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название промпта")
            return None

        if not text:
            QMessageBox.warning(self, "Ошибка", "Введите текст промпта")
            return None

        return {
            "name": name,
            "text": text
        }

    def center_relative_to_parent(self):
        """Центрирует окно относительно родительского окна."""
        if self.parent():
            parent_geometry = self.parent().geometry()
            parent_center = parent_geometry.center()
            
            # Получаем размеры текущего окна
            size = self.geometry()
            
            # Вычисляем позицию для центрирования
            x = parent_center.x() - size.width() // 2
            y = parent_center.y() - size.height() // 2
            
            # Перемещаем окно
            self.move(x, y)

    def apply_theme(self):
        """Применяет текущую тему к окну и всем его элементам."""
        if self.parent():
            theme_mode = self.parent().settings_manager.get_theme()
            style = get_style(theme_mode)
            self.setStyleSheet(style)
            self.update() 