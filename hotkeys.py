import traceback
import keyboard
import pyperclip
import time
import win32api
import win32con


def register_global_hotkeys(main_window, hotkey):
    """Функция для регистрации глобальных горячих клавиш"""

    def wait_for_keys_release():
        """Ждет, пока все клавиши-модификаторы не будут отпущены"""
        time.sleep(0.2)  # Даем время на отпускание клавиш после срабатывания хоткея
        modifiers = ["ctrl", "alt", "shift", "left windows", "right windows"]
        while any(keyboard.is_pressed(key) for key in modifiers):
            time.sleep(0.05)
        return True

    def send_ctrl_c():
        """Отправляет Ctrl+C через SendInput"""
        # Нажимаем Ctrl
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
        time.sleep(0.05)

        # Нажимаем C
        win32api.keybd_event(ord("C"), 0, 0, 0)
        time.sleep(0.05)

        # Отпускаем C
        win32api.keybd_event(ord("C"), 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)

        # Отпускаем Ctrl
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)
        # keyboard.send('ctrl+c')

    def on_hotkey_triggered():
        try:
            print("Функция on_hotkey_triggered вызвана")

            # Ждем отпускания всех клавиш пользователем
            print("Ожидание отпускания всех клавиш...")
            wait_for_keys_release()
            print("Все клавиши отпущены")

            # Получаем текущий текст из буфера обмена
            old_text = pyperclip.paste()

            # Эмулируем Ctrl+C через SendInput
            send_ctrl_c()
            time.sleep(0.2)  # Ждем обновления буфера обмена

            # Получаем новый текст из буфера
            text = pyperclip.paste()

            # Показываем окно приложения через сигнал
            main_window.show_window_requested.emit()

            # Проверяем, изменился ли текст
            if text and text != old_text:
                print(
                    f"Текст из буфера: {text[:100]}..."
                )  # Показываем первые 100 символов
                main_window.clipboard_updated.emit(text)
                print("Сигнал clipboard_updated отправлен")
            else:
                print("Буфер обмена не изменился или пуст")

        except Exception as e:
            print(f"Критическая ошибка в on_hotkey_triggered: {str(e)}")
            traceback.print_exc()

    # Регистрация горячей клавиши
    keyboard.add_hotkey(hotkey, on_hotkey_triggered)
    print(f"Глобальный хоткей '{hotkey}' успешно зарегистрирован.")


def unregister_global_hotkeys():
    """Функция для отмены регистрации глобальных горячих клавиш"""
    keyboard.unhook_all()
