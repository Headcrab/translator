import requests
import threading
import time
import logging
import llm_api

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def perform_translation(text):
    try:
        translated = llm_api.translate(text)
        logging.info("Перевод успешно выполнен")
        return translated
    except Exception as e:
        logging.error(f"Ошибка при выполнении перевода: {e}")
        return "Ошибка перевода"
