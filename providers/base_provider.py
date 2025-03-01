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
        
        # Получаем токен из переменной окружения или используем переданный
        access_token = model_info.get("access_token")
        print(f"\n=== Access token env variable name: {access_token}")
        
        if access_token:
            self.access_token = os.getenv(access_token, model_info.get("access_token", ""))
            print(f"=== Got token from env {access_token}: {'[PRESENT]' if self.access_token else '[MISSING]'}")
            if not self.access_token:
                print(f"=== WARNING: Environment variable {access_token} is not set or empty")
        else:
            # Если нет переменной окружения в настройках, пробуем стандартные
            provider = model_info.get("provider", "").lower()
            if provider == "openai":
                self.access_token = os.getenv("OPENAI_API_KEY", model_info.get("access_token", ""))
            elif provider == "anthropic":
                self.access_token = os.getenv("ANTHROPIC_API_KEY", model_info.get("access_token", ""))
            elif provider == "google":
                self.access_token = os.getenv("GOOGLE_API_KEY", model_info.get("access_token", ""))
            elif provider == "openrouter":
                self.access_token = os.getenv("OPENROUTER_API_KEY", model_info.get("access_token", ""))
            else:
                self.access_token = model_info.get("access_token", "")
            print(f"=== Got token for provider {provider}: {'[PRESENT]' if self.access_token else '[MISSING]'}")
        
        # Обновляем токен в model_info
        self.model_info["access_token"] = self.access_token
        print(f"=== Final token status: {'[PRESENT]' if self.access_token else '[MISSING]'}")
    
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

