"""Базовый класс для провайдеров LLM."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Coroutine

class BaseProvider(ABC):
    """Абстрактный базовый класс для всех провайдеров LLM."""
    
    def __init__(self, model_info: Dict[str, Any]):
        self.model_info = model_info
        self.api_endpoint = model_info["api_endpoint"]
        self.model_name = model_info["model_name"]
        self.access_token = model_info.get("access_token")
    
    @abstractmethod
    async def translate(
        self,
        messages: list,
        target_lang: str,
        streaming_callback: Optional[Callable[[str], Coroutine]] = None
    ) -> str:
        """Должен всегда возвращать строку (даже пустую)"""
        pass 

