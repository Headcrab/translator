import requests
import threading
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def run_background_http_request():
    """
    Пример фонового потока, который раз в несколько секунд опрашивает некий веб-сервис.
    Можно остановить по требованию.
    """

    def background_task():
        while True:
            try:
                # Пример запроса
                resp = requests.get("https://api.github.com")
                if resp.status_code == 200:
                    print("Успешный ответ:", resp.json())
                else:
                    print(f"Ошибка: статус {resp.status_code}")
            except Exception as e:
                print("Ошибка HTTP-запроса:", e)

            # Пауза на 10 секунд
            time.sleep(10)

    # Запускаем поток
    t = threading.Thread(target=background_task, daemon=True)
    t.start()

def perform_translation(text):
    try:
        translated = llm_api.translate(text)
        logging.info("Перевод успешно выполнен")
        return translated
    except Exception as e:
        logging.error(f"Ошибка при выполнении перевода: {e}")
        return "Ошибка перевода"
