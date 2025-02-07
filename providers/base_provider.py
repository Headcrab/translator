"""Базовый класс для провайдеров LLM."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Coroutine, List
import os

class BaseProvider(ABC):
    """Абстрактный базовый класс для всех провайдеров LLM."""
    
    def __init__(self, model_info: Dict[str, Any]):
        self.model_info = model_info
        self.api_endpoint = model_info["api_endpoint"]
        self.model_name = model_info["model_name"]
        self.access_token = model_info.get("access_token")
        
        # Переопределяем токен, используя переменные окружения, если они заданы
        provider = model_info.get("provider", "").lower()
        if provider == "openai":
            self.access_token = os.getenv("OPENAI_API_KEY", self.access_token)
        elif provider == "anthropic":
            self.access_token = os.getenv("ANTHROPIC_API_KEY", self.access_token)
        elif provider == "google":
            self.access_token = os.getenv("GOOGLE_API_KEY", self.access_token)
        elif provider == "openrouter":
            self.access_token = os.getenv("OPENROUTER_API_KEY", self.access_token)
        
        self.model_info["access_token"] = self.access_token
    
    @abstractmethod
    async def translate(
        self,
        messages: list,
        target_lang: str,
        streaming_callback: Optional[Callable[[str], Coroutine]] = None
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

