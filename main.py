import sys
import traceback
import threading
import asyncio
import argparse
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from ui.system_tray import SystemTrayHandler
from hotkeys import register_global_hotkeys
from settings_manager import SettingsManager
from qasync import QEventLoop
import logging
from PyQt5.QtNetwork import QLocalServer, QLocalSocket
from PyQt5.QtCore import QObject, pyqtSignal

# Глобальная переменная для debug режима
DEBUG_MODE = True


def setup_logging(debug_mode=False):
    """Настройка логирования в зависимости от режима."""
    if debug_mode:
        # В debug режиме показываем все включая HTTP запросы
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
            ],
        )
        # Включаем debug для HTTP клиентов
        logging.getLogger("aiohttp").setLevel(logging.DEBUG)
        logging.getLogger("openai").setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)
        print("=== DEBUG MODE ENABLED ===")
        print("HTTP requests and responses will be logged to console")
        print("=" * 50)
    else:
        # Обычный режим - только ошибки
        logging.basicConfig(
            level=logging.ERROR,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )


class SingleInstanceHandler(QObject):
    new_instance_started = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.server = QLocalServer()
        self.server.newConnection.connect(self._handle_new_connection)

    def _handle_new_connection(self):
        socket = self.server.nextPendingConnection()
        if socket.waitForReadyRead(1000):
            self.new_instance_started.emit()
        socket.disconnectFromServer()

    def listen(self, server_name):
        # Удаляем старый сервер, если он существует
        QLocalServer.removeServer(server_name)
        return self.server.listen(server_name)


def try_connect_to_running_instance(server_name):
    socket = QLocalSocket()
    socket.connectToServer(server_name, QLocalSocket.ReadWrite)
    if socket.waitForConnected(1000):
        # Отправляем сигнал существующему экземпляру
        socket.write(b"show")
        socket.flush()
        socket.waitForBytesWritten(1000)
        socket.disconnectFromServer()
        return True
    return False


if __name__ == "__main__":
    try:
        # Парсинг аргументов командной строки
        parser = argparse.ArgumentParser(description="LLM Translator")
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug mode with detailed HTTP logging",
        )
        args = parser.parse_args()

        # Устанавливаем глобальный debug режим
        DEBUG_MODE = args.debug
        setup_logging(DEBUG_MODE)

        server_name = "LLM_Translator_Server"

        # Пробуем подключиться к существующему экземпляру
        if try_connect_to_running_instance(server_name):
            sys.exit(0)

        # Создаём экземпляр QApplication
        app = QApplication(sys.argv)
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)

        # Убедиться в инициализации event loop
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        with loop:
            # Инициализируем главное окно
            window = MainWindow()
            window.show()

            # Инициализация системного трея
            tray_handler = SystemTrayHandler(app, window)
            tray_handler.show()

            # Создаем обработчик единственного экземпляра
            single_instance = SingleInstanceHandler()
            single_instance.new_instance_started.connect(window.show_window)
            if not single_instance.listen(server_name):
                print("Failed to start single instance server")

            # Регистрация горячих клавиш
            settings_manager = SettingsManager()
            modifiers, key = settings_manager.get_hotkey()
            hotkey = "+".join(modifiers) + "+" + key if modifiers else key
            hotkey_thread = threading.Thread(
                target=register_global_hotkeys, args=(window, hotkey), daemon=True
            )
            hotkey_thread.start()

            loop.run_forever()

    except Exception as e:
        print(f"Critical error: {e}")
        traceback.print_exc()
    finally:
        if "loop" in locals():
            loop.close()
