"""Модуль для работы с API различных LLM моделей."""

import os
import json
import aiohttp
import asyncio
from typing import Optional, Dict, Any
import requests
from settings_manager import SettingsManager

class LLMApi:
    """Класс для работы с API различных LLM моделей."""
    
    def __init__(self, model_info: Dict[str, Any], settings_manager: SettingsManager):
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
        self.settings_manager = settings_manager
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
            
        system_prompt = self.settings_manager.get_system_prompt()
        
        messages = [
            {
                "role": "system",
                "content": system_prompt.format(language=target_lang)
            },
            {
                "role": "user", 
                "content": text
            }
        ]
        
        try:
            if self.provider == "OpenAI":
                return await self._translate_openai(messages)
            elif self.provider == "Anthropic":
                return await self._translate_anthropic(messages)
            elif self.provider == "OpenRouter":
                return await self._translate_openrouter(messages)
            else:
                raise ValueError(f"Неподдерживаемый провайдер: {self.provider}")
        except Exception as e:
            raise Exception(f"Ошибка при переводе: {str(e)}")
            
    async def _translate_openai(self, messages: list) -> str:
        """Перевод через OpenAI API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        data = {
            "model": self.model_name,
            "messages": messages,
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
                
    async def _translate_anthropic(self, messages: list) -> str:
        """Перевод через Anthropic API."""
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": self.access_token
        }
        
        data = {
            "model": self.model_name,
            "prompt": f"\n\nHuman: {messages[-1]['content']}\n\nAssistant:",
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
                
    async def _translate_openrouter(self, messages: list) -> str:
        """Перевод через OpenRouter API."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        
        data = {
            "model": self.model_name,
            "messages": messages
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

def translate(text):
    # Пример реализации перевода с использованием внешнего API
    try:
        response = requests.post("https://api.translate.com/translate", data={"text": text})
        response.raise_for_status()
        return response.json().get("translated_text", "")
    except requests.RequestException as e:
        # Логирование ошибки
        print(f"Ошибка при переводе: {e}")
        return "Ошибка перевода"

