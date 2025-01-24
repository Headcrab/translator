import sys
import traceback
import threading
from PyQt5.QtWidgets import QApplication
from gui import MainWindow
from system_tray import SystemTrayHandler
from hotkeys import register_global_hotkeys
from settings_manager import SettingsManager
# from background_tasks import run_background_http_request


def main():
    # Создаём экземпляр QApplication
    app = QApplication(sys.argv)

    # Инициализируем главное окно
    main_window = MainWindow()

    # Иконка в системном трее
    tray_handler = SystemTrayHandler(app, main_window)
    tray_handler.show()

    # Загрузка настроек
    settings_manager = SettingsManager()
    modifiers, key = settings_manager.get_hotkey()

    # Формируем строку хоткея
    hotkey = "+".join(modifiers) + "+" + key if modifiers else key

    # Регистрация глобальных горячих клавиш в отдельном потоке
    hotkey_thread = threading.Thread(
        target=register_global_hotkeys, args=(main_window, hotkey), daemon=True
    )
    hotkey_thread.start()

    # Запускаем фоновый поток с HTTP-запросами (по желанию)
    # run_background_http_request()

    # Запуск основного цикла
    sys.exit(app.exec_())


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Неожиданная ошибка при запуске приложения:", e)
        traceback.print_exc()
