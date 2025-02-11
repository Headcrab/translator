import os
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QMainWindow
from PyQt5.QtGui import QIcon
from ui import resources_rc  # Добавляем импорт ресурсов


class SystemTrayHandler:
    """
    Класс для иконки в системном трее, с контекстным меню и обработчиками.
    """

    def __init__(self, app, window):
        self.app = app
        self.window = window
        try:
            self.tray_icon = QSystemTrayIcon()

            # Установка иконки из ресурсов Qt
            self.tray_icon.setIcon(QIcon(":/icons/icon.png"))

            # Определяем все методы до их использования
            def show_main_window(self):
                """Показать главное окно приложения."""
                self.window.showNormal()
                self.window.activateWindow()

            def show_settings_window(self):
                """Показать окно настроек."""
                self.window.settings_window.show()

            def show(self):
                """Отобразить иконку в трее."""
                self.tray_icon.show()

            def exit_app(self):
                """Завершить работу приложения."""
                # Отключаем хоткеи, если нужно
                # keyboard.unhook_all() # TODO: перенести в модуль hotkeys
                self.app.quit()

            def on_tray_icon_activated(self, reason):
                """
                Обработка кликов по иконке в трее.
                reason может быть:
                - QSystemTrayIcon.Trigger (обычный клик)
                - QSystemTrayIcon.DoubleClick (двойной клик)
                и т.д.
                """
                if reason == QSystemTrayIcon.DoubleClick:
                    # Однократный клик по иконке – показываем/скрываем окно
                    if self.window.isVisible():
                        self.window.hide()
                    else:
                        self.show_main_window()

            # Сохраняем все методы как атрибуты класса
            self.show_main_window = show_main_window.__get__(self)
            self.show_settings_window = show_settings_window.__get__(self)
            self.show = show.__get__(self)
            self.exit_app = exit_app.__get__(self)
            self.on_tray_icon_activated = on_tray_icon_activated.__get__(self)

            # Создаём меню трея
            self.menu = QMenu()

            open_action = QAction("Открыть окно", self.menu)
            open_action.triggered.connect(self.show_main_window)
            self.menu.addAction(open_action)

            settings_action = QAction("Настройки", self.menu)
            settings_action.triggered.connect(self.show_settings_window)
            self.menu.addAction(settings_action)

            # Разделитель
            self.menu.addSeparator()

            exit_action = QAction("Выход", self.menu)
            exit_action.triggered.connect(self.exit_app)
            self.menu.addAction(exit_action)

            self.tray_icon.setContextMenu(self.menu)
            self.tray_icon.setToolTip("LLM Translator")
            self.tray_icon.activated.connect(self.on_tray_icon_activated)
        except Exception as e:
            print(f"Tray init error: {e}")
            self.tray_icon = None

    def show(self):
        if self.tray_icon:
            self.tray_icon.show()
