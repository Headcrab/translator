import sys
import traceback
import threading
import asyncio
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from system_tray import SystemTrayHandler
from hotkeys import register_global_hotkeys
from settings_manager import SettingsManager
from qasync import QEventLoop


def main():
    # Создаём экземпляр QApplication
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # Убедиться в инициализации event loop
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Инициализируем главное окно
    window = MainWindow()
    window.show()

    # Иконка в системном трее
    tray_handler = SystemTrayHandler(app, window)
    tray_handler.show()

    # Загрузка настроек
    settings_manager = SettingsManager()
    modifiers, key = settings_manager.get_hotkey()

    # Формируем строку хоткея
    hotkey = "+".join(modifiers) + "+" + key if modifiers else key

    # Регистрация глобальных горячих клавиш в отдельном потоке
    hotkey_thread = threading.Thread(
        target=register_global_hotkeys, args=(window, hotkey), daemon=True
    )
    hotkey_thread.start()

    # Запускаем фоновый поток с HTTP-запросами (по желанию)
    # run_background_http_request()

    # Запуск основного цикла
    with loop:
        loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Неожиданная ошибка при запуске приложения:", e)
        traceback.print_exc()
