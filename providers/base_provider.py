"""Базовый класс для провайдеров LLM."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Coroutine, List
import os
import logging
import aiohttp
import json

logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """Абстрактный базовый класс для всех провайдеров LLM."""

    def __init__(self, model_info: Dict[str, Any]):
        if not isinstance(model_info, dict):
            raise TypeError("model_info должен быть словарем")

        self.model_name = model_info.get("model_name")
        self.access_token = model_info.get("access_token")
        self.api_endpoint = model_info.get("api_endpoint")
        self.model_info = model_info

    def _is_debug_mode(self) -> bool:
        """Проверяет включен ли debug режим."""
        import main

        return getattr(main, "DEBUG_MODE", False)

    async def _log_http_request(
        self, method: str, url: str, headers: dict, data: dict = None
    ) -> None:
        """Логирует HTTP запрос в debug режиме."""
        if not self._is_debug_mode():
            return

        logger.debug(f"\n{'=' * 80}")
        logger.debug(f"🔄 HTTP REQUEST: {method} {url}")
        logger.debug(f"{'=' * 80}")

        # Показываем ВСЕ заголовки включая API ключи
        logger.debug("📋 HEADERS (FULL - INCLUDING API KEYS):")
        for key, value in headers.items():
            logger.debug(f"  {key}: {value}")

        # Показываем тело запроса
        if data:
            logger.debug(f"\n📤 REQUEST BODY:")
            if isinstance(data, dict):
                logger.debug(json.dumps(data, indent=2, ensure_ascii=False))
            else:
                logger.debug(str(data))

        logger.debug(f"{'=' * 80}")

    async def _log_http_response(
        self, response: aiohttp.ClientResponse, response_text: str
    ) -> None:
        """Логирует HTTP ответ в debug режиме."""
        if not self._is_debug_mode():
            return

        logger.debug(f"\n{'=' * 80}")
        logger.debug(f"📨 HTTP RESPONSE: {response.status} {response.reason}")
        logger.debug(f"{'=' * 80}")

        # Показываем ВСЕ заголовки ответа
        logger.debug("📋 RESPONSE HEADERS:")
        for key, value in response.headers.items():
            logger.debug(f"  {key}: {value}")

        # Показываем тело ответа
        logger.debug(f"\n📥 RESPONSE BODY:")
        try:
            # Пытаемся распарсить как JSON для красивого вывода
            parsed_json = json.loads(response_text)
            logger.debug(json.dumps(parsed_json, indent=2, ensure_ascii=False))
        except:
            # Если не JSON, показываем как есть
            logger.debug(response_text)

        logger.debug(f"{'=' * 80}\n")

    async def _handle_http_error(
        self, response: aiohttp.ClientResponse, operation: str = "API request"
    ) -> None:
        """
        Обрабатывает HTTP ошибки с понятными сообщениями для пользователя.

        Args:
            response: HTTP ответ с ошибкой
            operation: Описание операции для контекста ошибки
        """
        # Логируем ошибку в debug режиме
        error_text = ""
        try:
            error_text = await response.text()
            await self._log_http_response(response, error_text)
        except:
            pass

        provider_name = self.__class__.__name__.replace("Provider", "")

        if response.status == 401:
            raise Exception(
                f"API ключ {provider_name} недействителен. "
                f"Проверьте ключ в настройках и перезапустите приложение. "
                f"(HTTP {response.status})"
            )
        elif response.status == 403:
            raise Exception(
                f"Доступ запрещен для {provider_name}. "
                f"Проверьте права API ключа. (HTTP {response.status})"
            )
        elif response.status == 429:
            raise Exception(
                f"Превышена квота запросов для {provider_name}. "
                f"Попробуйте позже. (HTTP {response.status})"
            )
        elif response.status == 500:
            raise Exception(
                f"Внутренняя ошибка сервера {provider_name}. "
                f"Попробуйте позже. (HTTP {response.status})"
            )
        else:
            # Показываем детали ошибки в debug режиме
            error_details = (
                f" - {error_text[:200]}..."
                if error_text and self._is_debug_mode()
                else ""
            )
            raise Exception(
                f"Ошибка {operation} в {provider_name}: "
                f"HTTP {response.status}{error_details}"
            )

    @abstractmethod
    async def translate(
        self,
        messages: list,
        target_lang: str,
        streaming_callback: Optional[Callable[[str], Coroutine]] = None,
    ) -> str:
        """Переводит текст с использованием LLM API."""
        pass

    @abstractmethod
    async def get_available_models(self) -> List[str]:
        """Получает список доступных моделей."""
        pass
