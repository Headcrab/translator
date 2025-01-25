"""Модуль для работы с API различных LLM моделей."""

import os
import json
import aiohttp
import asyncio
from typing import Optional, Dict, Any

class LLMApi:
    """Класс для работы с API различных LLM моделей."""
    
    def __init__(self, model_info: Dict[str, Any]):
        """
        Инициализация клиента API.
        
        Args:
            model_info: Словарь с информацией о модели:
                - name: Имя модели
                - provider: Провайдер (OpenAI, Anthropic, OpenRouter)
                - api_endpoint: URL эндпоинта API
                - model_name: Название модели у провайдера
                - access_token: Токен доступа к API
        """
        self.model_info = model_info
        self.provider = model_info["provider"]
        self.api_endpoint = model_info["api_endpoint"]
        self.model_name = model_info["model_name"]
        self.access_token = model_info.get("access_token")
        
    async def translate(self, text: str, target_lang: str) -> str:
        """
        Переводит текст на указанный язык используя выбранную модель.
        
        Args:
            text: Исходный текст для перевода
            target_lang: Язык, на который нужно перевести
            
        Returns:
            str: Переведенный текст
            
        Raises:
            Exception: При ошибке перевода
        """
        if not text:
            return ""
            
        prompt = f"Переведи следующий текст на {target_lang}:\n\n{text}"
        
        try:
            if self.provider == "OpenAI":
                return await self._translate_openai(prompt)
            elif self.provider == "Anthropic":
                return await self._translate_anthropic(prompt)
            elif self.provider == "OpenRouter":
                return await self._translate_openrouter(prompt)
            else:
                raise ValueError(f"Неподдерживаемый провайдер: {self.provider}")
        except Exception as e:
            raise Exception(f"Ошибка при переводе: {str(e)}")
            
    async def _translate_openai(self, prompt: str) -> str:
        """Перевод через OpenAI API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_endpoint}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API вернул ошибку {response.status}: {error_text}")
                    
                result = await response.json()
                return result["choices"][0]["message"]["content"].strip()
                
    async def _translate_anthropic(self, prompt: str) -> str:
        """Перевод через Anthropic API."""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.access_token
        }
        
        data = {
            "model": self.model_name,
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_endpoint}/v1/complete",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Anthropic API вернул ошибку {response.status}: {error_text}")
                    
                result = await response.json()
                return result["completion"].strip()
                
    async def _translate_openrouter(self, prompt: str) -> str:
        """Перевод через OpenRouter API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.api_endpoint,
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"OpenRouter API вернул ошибку {response.status}: {error_text}")
                    
                result = await response.json()
                return result["choices"][0]["message"]["content"].strip() 