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
import logging

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main_async():
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
    return 0


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)
        
        with loop:
            window = MainWindow()
            window.show()
            
            # Инициализация системного трея
            tray_handler = SystemTrayHandler(app, window)
            tray_handler.show()

            # Регистрация горячих клавиш
            settings_manager = SettingsManager()
            modifiers, key = settings_manager.get_hotkey()
            hotkey = "+".join(modifiers) + "+" + key if modifiers else key
            hotkey_thread = threading.Thread(
                target=register_global_hotkeys, 
                args=(window, hotkey),
                daemon=True
            )
            hotkey_thread.start()

            loop.run_forever()
            
    except Exception as e:
        print(f"Critical error: {e}")
        traceback.print_exc()
    finally:
        if 'loop' in locals():
            loop.close()
