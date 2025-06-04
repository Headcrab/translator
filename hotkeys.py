import traceback
import keyboard
import pyperclip
import time
import logging


def register_global_hotkeys(window, hotkey):
    """Функция для регистрации глобальных горячих клавиш"""
    # print(f"Регистрируем хоткей: {hotkey}")

    def wait_for_keys_release():
        """Ждет, пока все клавиши-модификаторы не будут отпущены"""
        time.sleep(0.2)  # Даем время на отпускание клавиш после срабатывания хоткея
        modifiers = ["ctrl", "alt", "shift", "left windows", "right windows"]
        while any(keyboard.is_pressed(key) for key in modifiers):
            time.sleep(0.05)
        return True

    def send_ctrl_c():
        """Отправляет Ctrl+C в кросс-платформенном варианте."""
        try:
            keyboard.send("ctrl+c")
        except Exception as e:
            logging.error("Failed to send Ctrl+C: %s", e)

    def on_hotkey_triggered():
        try:
            logging.debug("Функция on_hotkey_triggered вызвана")

            # Ждем отпускания всех клавиш пользователем
            logging.debug("Ожидание отпускания всех клавиш...")
            wait_for_keys_release()
            logging.debug("Все клавиши отпущены")

            # Получаем текущий текст из буфера обмена
            old_text = pyperclip.paste()

            # Эмулируем Ctrl+C через SendInput
            send_ctrl_c()
            time.sleep(0.2)  # Ждем обновления буфера обмена

            # Получаем новый текст из буфера
            text = pyperclip.paste()

            # Показываем окно приложения через сигнал
            window.show_window_requested.emit()

            # Проверяем, изменился ли текст
            if text and text != old_text:
                logging.debug("Текст из буфера: %s...", text[:100])
                window.clipboard_updated.emit(text)
                logging.debug("Сигнал clipboard_updated отправлен")
            else:
                logging.debug("Буфер обмена не изменился или пуст")

        except Exception as e:
            logging.error("Критическая ошибка в on_hotkey_triggered: %s", e)
            traceback.print_exc()

    # Регистрация горячей клавиши
    keyboard.add_hotkey(hotkey, on_hotkey_triggered)
    logging.info("Глобальный хоткей '%s' успешно зарегистрирован.", hotkey)


def unregister_global_hotkeys():
    """Функция для отмены регистрации глобальных горячих клавиш"""
    keyboard.unhook_all()
