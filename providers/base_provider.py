"""Базовый класс для провайдеров LLM."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Coroutine, List
import os
import logging


class BaseProvider(ABC):
    """Абстрактный базовый класс для всех провайдеров LLM."""

    def __init__(self, model_info: Dict[str, Any]):
        self.model_info = model_info
        self.api_endpoint = model_info["api_endpoint"]
        self.model_name = model_info["model_name"]

        # Получаем токен и сохраняем в конфигурации модели
        self.access_token = self._extract_access_token(model_info)
        self.model_info["access_token"] = self.access_token

    def _extract_access_token(self, model_info: Dict[str, Any]) -> str:
        """Возвращает токен доступа для указанной конфигурации модели."""
        access_token_env = model_info.get("access_token")
        logging.debug("Access token env variable name: %s", access_token_env)

        if access_token_env:
            token = os.getenv(access_token_env, model_info.get("access_token", ""))
            logging.debug(
                "Got token from env %s: %s",
                access_token_env,
                "[PRESENT]" if token else "[MISSING]",
            )
            if not token:
                logging.warning("Environment variable %s is not set", access_token_env)
            return token

        provider = model_info.get("provider", "").lower()
        env_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "google": "GOOGLE_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
        }
        env_var = env_map.get(provider)
        token = os.getenv(env_var, "") if env_var else ""
        if not token:
            token = model_info.get("access_token", "")
        logging.debug(
            "Got token for provider %s: %s",
            provider,
            "[PRESENT]" if token else "[MISSING]",
        )
        return token

    @abstractmethod
    async def translate(
        self,
        messages: list,
        target_lang: str,
        streaming_callback: Optional[Callable[[str], Coroutine]] = None,
    ) -> str:
        """Должен всегда возвращать строку (даже пустую)"""
        pass

    @abstractmethod
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Возвращает список доступных моделей от провайдера.

        Returns:
            List[Dict[str, Any]]: Список словарей с информацией о моделях.
            Каждый словарь должен содержать как минимум:
            - name: str - Название модели
            - model_name: str - Идентификатор модели у провайдера
            - description: str - Описание модели
        """
        pass
